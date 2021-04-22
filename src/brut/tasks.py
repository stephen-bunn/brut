# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains executable tasks for the application."""

import shutil
from datetime import datetime
from pathlib import Path

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from megu.filters import best_content
from megu.helpers import temporary_directory
from megu.services import get_downloader, get_plugin, iter_content, merge_manifest

from .db import Artifact, Content, db_session
from .env import instance as env
from .hasher import HashType, hash_file
from .helpers import setup_logging
from .log import instance as log
from .watchers import get_watcher

# brut.tasks is an entrypoint for workers, ensure logging is setup early
setup_logging()

# setup backend and broker for dramatiq actors prior to defining actors
# must occur before the @dramatiq.actor decorator is used or you will never get task
# messages being read from Redis
redis_backend = RedisBackend()
redis_broker = RedisBroker(url=env.redis.url)
redis_broker.add_middleware(Results(backend=redis_backend))

dramatiq.set_broker(redis_broker)


@dramatiq.actor
def watch(watcher_type: str, *args, **kwargs):
    """Job responsible for getting new content entries and adding them to the db.

    Args:
        watcher_type (str):
            The type of watcher to use for extracting content.]
    """

    watcher = get_watcher(watcher_type)
    if watcher is None:
        log.error(f"Failed to determine the appropriate watcher for {watcher_type!r}")
        return None

    with db_session() as session:
        for content in watcher().iter_content(*args, **kwargs):

            # skip content if content matching the fingerprint already exists
            if session.query(
                session.query(Content)
                .filter(Content.fingerprint == content.fingerprint)
                .exists()
            ).scalar():
                log.debug(
                    f"Skipping content {content.url} ({content.fingerprint}) "
                    "as it already exists"
                )
                continue

            log.info(f"Adding content {content.url} ({content.fingerprint})")
            session.add(content)

        session.commit()


@dramatiq.actor
def enqueue():
    """Job responsible for enqueing non-processed content to be fetched."""

    with db_session() as session:
        for content in session.query(Content).filter(
            Content.processed_at == None  # noqa
        ):
            log.debug(
                f"Enqueuing content {content.url} ({content.fingerprint}) to be fetched"
            )

            fetch.send(content.id, content.url)


@dramatiq.actor
def fetch(content_id: int, url: str):
    with db_session() as session:
        db_content = session.query(Content).get(content_id)
        if not db_content:
            log.error(f"Could not find content {content_id} in the database")
            return

        db_content.processed_at = datetime.now()
        plugin = get_plugin(url)
        if not plugin:
            db_content.processed_message = "unhandled"
            return

        store_path = env.store_path
        if not store_path.is_dir():
            log.info(f"Creating store directory at {store_path}")
            store_path.mkdir()

        try:
            for content in best_content(iter_content(url, plugin)):
                downloader = get_downloader(content)
                manifest = downloader.download_content(content)

                with temporary_directory("brut") as temp_dir:
                    temp_path = temp_dir / content.filename
                    merge_manifest(plugin, manifest, temp_path)

                    checksum = hash_file(temp_path, {HashType.XXHASH})[HashType.XXHASH]
                    fragment_path = Path(checksum[0]) / Path(checksum[1:3])

                    to_path = store_path / fragment_path / content.filename
                    if to_path.exists():
                        if len(content.checksums) <= 0:
                            log.warning(
                                f"Skipping content since {to_path!s} already exists"
                            )
                            db_content.processed_message = "skipped"
                            continue

                        first_checksum = content.checksums[0]
                        hash_type = HashType(first_checksum.type)
                        if (
                            hash_file(to_path, {hash_type})[hash_type]
                            == first_checksum.hash
                        ):
                            log.warning(
                                f"Skipping content since {to_path} already exists and "
                                f"checksum {first_checksum.hash} verified"
                            )
                            db_content.processed_message = "skipped"
                            continue

                    if not to_path.parent.is_dir():
                        log.info(
                            f"Creating store fragment directory at {to_path.parent}"
                        )
                        to_path.parent.mkdir(parents=True)

                    log.debug(
                        f"Copying downloaded content at {temp_path!s} to {to_path!s}"
                    )
                    shutil.copy(temp_path, to_path)

                    db_content.processed_message = None

                    # setup artifact in the database
                    db_artifact = Artifact(
                        created_at=datetime.now(),
                        fingerprint=checksum,
                    )
                    db_artifact.content_id = content_id
                    session.add(db_artifact)

        except Exception as exc:
            log.exception(str(exc))
            db_content.processed_message = str(exc)
