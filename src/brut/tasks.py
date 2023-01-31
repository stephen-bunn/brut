import shutil
from pathlib import Path

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from megu import download_content, get_downloader, get_plugin, iter_content, write_content
from megu.filters import best_content
from megu.hash import HashType, hash_file
from megu.helpers import temporary_directory
from megu.models import URL
from megu.plugin.generic import GenericPlugin

from brut.config import get_config
from brut.db import client
from brut.env import get_env
from brut.log import get_logger
from brut.watcher import get_watcher

ARTIFACT_PATH_STRATEGY = [slice(0, 2), slice(2, 4)]


env = get_env()
log = get_logger()
conf = get_config()

redis_backend = RedisBackend()
redis_broker = RedisBroker(url=env.redis_url)
redis_broker.add_middleware(Results(backend=redis_backend))
dramatiq.set_broker(redis_broker)


def _build_artifact_filepath(checksum: str, suffix: str | None = None) -> Path:
    return (
        Path(*[checksum[fragment_slice] for fragment_slice in ARTIFACT_PATH_STRATEGY])
        .joinpath(checksum)
        .with_suffix(suffix or "")
    )


@dramatiq.actor
def watch(watcher_type: str, *args, **kwargs):
    watcher = get_watcher(watcher_type)
    if watcher is None:
        log.error(f"Could not determine watcher for type {watcher_type}")
        return

    log.info(f"Polling for new content with watcher {watcher.type} ({args}, {kwargs})")
    for artifact in watcher().iter_artifacts(*args, **kwargs):
        log.info(f"Adding artifact {artifact.fingerprint} ({artifact.url})")


@dramatiq.actor
def fetch(artifact_fingerprint: str):
    with client.db_session(env.database_path) as session:
        artifact = client.get_artifact(session, artifact_fingerprint)
        if artifact is None:
            log.error(f"Could not find artifact {artifact_fingerprint}")
            return

        artifact_url = URL(artifact.url)
        plugin = get_plugin(artifact_url, env.megu.plugin_dir)
        if isinstance(plugin, GenericPlugin):
            client.mark_artifact_fetched(session, artifact, "unhandled")
            return

        store_dirpath = Path(env.store_dir)
        if not store_dirpath.is_dir():
            log.debug(f"Creating store directory at {store_dirpath}")
            store_dirpath.mkdir(parents=True)

        try:
            for content in best_content(iter_content(plugin, artifact.url)):
                downloader = get_downloader(content)
                content_manifest = download_content(downloader, content)

                with temporary_directory("brut") as temp_dirpath:
                    temp_filepath = temp_dirpath.joinpath(content.filename)
                    write_content(plugin, content_manifest, temp_filepath)

                    checksum = hash_file(temp_filepath, {HashType.SHA1})[HashType.SHA1]
                    to_path = env.store_dir.joinpath(
                        _build_artifact_filepath(checksum, temp_filepath.suffix)
                    )

                    if to_path.exists():
                        if len(content.checksums) > 0:
                            content_checksum = content.checksums[0]
                            content_checksum_type = HashType(content_checksum.type)

                            if (
                                hash_file(to_path, {content_checksum_type})[content_checksum_type]
                                == content_checksum.value
                            ):
                                log.warning(
                                    f"Skipping artifact {artifact.fingerprint} as {to_path} "
                                    "already exists and is checksum verified"
                                )
                                client.mark_artifact_fetched(session, artifact, "skipped")

                    if not to_path.parent.is_dir():
                        log.debug(f"Creating store fragment directory at {to_path.parent}")
                        to_path.parent.mkdir(parents=True)

                    shutil.move(temp_filepath, to_path)
                    client.mark_artifact_fetched(session, artifact, "success")
                    log.info(f"Fetched artifact {artifact.fingerprint} to {to_path}")

        except Exception as error:
            log.exception(str(error))


@dramatiq.actor
def enqueue():
    with client.db_session(env.database_path) as session:
        for artifact in client.iter_unprocessed_artifacts(session):
            log.info(f"Enqueing artifact {artifact.fingerprint} for fetch")
            fetch.send(artifact.fingerprint)
            client.mark_artifact_processed(session, artifact, "success")
