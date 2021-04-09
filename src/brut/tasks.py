# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains executable tasks for the application."""

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

from .db import Content, db_session
from .env import instance as env
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
