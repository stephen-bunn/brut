import sqlite3
from contextlib import contextmanager, suppress
from datetime import datetime
from pathlib import Path
from typing import Generator, Iterator, cast
from uuid import uuid4

from caribou import downgrade, upgrade
from pydapper.commands import Commands
from pydapper.exceptions import NoResultException
from pydapper.main import using
from pydapper.types import ConnectionType
from pypika import Query, Table

from brut.db.models import Artifact

CHANGES_DIRPATH = Path(__file__).parent.joinpath("changes").absolute()

T_ARTIFACT = Table("artifact")


def db_migrate(
    db_path: Path,
    version: str | None = None,
    is_downgrade: bool = False,
):
    if not CHANGES_DIRPATH.is_dir():
        raise NotADirectoryError(f"Database changes directory not found at {CHANGES_DIRPATH}")

    handler = upgrade if not is_downgrade else downgrade
    handler(db_path.as_posix(), CHANGES_DIRPATH.as_posix(), version)


@contextmanager
def db_session(
    db_path: Path,
    autocommit: bool = True,
) -> Generator[Commands, None, None]:
    connection = sqlite3.connect(db_path.as_posix())
    try:
        yield using(cast(ConnectionType, connection))
        if autocommit:
            connection.commit()
    finally:
        connection.close()


def iter_unprocessed_artifacts(commands: Commands) -> Iterator[Artifact]:
    query = Query.from_(T_ARTIFACT).select(T_ARTIFACT.star).where(T_ARTIFACT.processed_at.isnull())
    yield from commands.query(str(query), model=Artifact, buffered=True)


def iter_unfetched_artifacts(commands: Commands) -> Iterator[Artifact]:
    query = Query.from_(T_ARTIFACT).select(T_ARTIFACT.star).where(T_ARTIFACT.fetched_at.isnull())
    yield from commands.query(str(query), model=Artifact, buffered=True)


def get_artifact(commands: Commands, fingerprint: str) -> Artifact | None:
    query = (
        Query.from_(T_ARTIFACT).select(T_ARTIFACT.star).where(T_ARTIFACT.fingerprint == fingerprint)
    )

    with suppress(NoResultException):
        return commands.query_first(str(query), model=Artifact)

    return None


def artifact_exists(commands: Commands, fingerprint: str) -> bool:
    query = Query.from_(T_ARTIFACT).select("1").where(T_ARTIFACT.fingerprint == fingerprint)
    with suppress(NoResultException):
        return commands.execute_scalar(str(query)) is not None

    return False


def create_artifact(commands: Commands, url: str) -> Artifact:
    artifact_id = uuid4()
    artifact_fingerprint = Artifact.build_fingerprint(url)
    created_at = datetime.utcnow()
    query = Query.into(T_ARTIFACT).insert(
        artifact_id,
        created_at,
        artifact_fingerprint,
        url,
        None,
        None,
        None,
        None,
    )

    commands.execute(str(query))
    return Artifact(artifact_id, created_at, artifact_fingerprint, url)


def ensure_artifact(commands: Commands, url: str) -> Artifact:
    artifact = get_artifact(commands, Artifact.build_fingerprint(url))
    if artifact is not None:
        return artifact

    return create_artifact(commands, url)


def mark_artifact_processed(
    commands: Commands,
    artifact: Artifact,
    processed_message: str,
) -> Artifact:
    artifact_processed_at = datetime.utcnow()
    query = (
        Query.update(T_ARTIFACT)
        .set(T_ARTIFACT.processed_at, artifact_processed_at)
        .set(T_ARTIFACT.processed_message, processed_message)
        .where(T_ARTIFACT.id == artifact.id)
    )

    commands.execute(str(query))
    artifact.processed_at = artifact_processed_at
    artifact.processed_message = processed_message
    return artifact


def mark_artifact_fetched(
    commands: Commands,
    artifact: Artifact,
    fetched_message: str,
) -> Artifact:
    artifact_fetched_at = datetime.utcnow()
    query = (
        Query.update(T_ARTIFACT)
        .set(T_ARTIFACT.fetched_at, artifact_fetched_at)
        .set(T_ARTIFACT.fetched_message, fetched_message)
        .where(T_ARTIFACT.id == artifact.id)
    )

    commands.execute(str(query))
    artifact.fetched_at = artifact_fetched_at
    artifact.fetched_message = fetched_message
    return artifact
