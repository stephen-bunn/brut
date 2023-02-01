"""Contains database client helpers and operations."""

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
"""The directory that library-bundled database changes (migrations) live in."""

T_ARTIFACT = Table("artifact")
"""The artifact table reference."""


def db_migrate(
    db_path: Path,
    version: str | None = None,
    is_downgrade: bool = False,
):
    """Migrate the database at the given filepath.

    By default this will attempt to upgrade the database to the newest version.

    Args:
        db_path (Path):
            The database filepath to migrate.
        version (str | None, optional):
            The version to migrate the database to. Defaults to None.
        is_downgrade (bool, optional):
            True if the migration should be treated as a downgrade. Defaults to False.

    Raises:
        NotADirectoryError: If the database changes directory does not exist.
    """

    if not CHANGES_DIRPATH.is_dir():
        raise NotADirectoryError(f"Database changes directory not found at {CHANGES_DIRPATH}")

    handler = upgrade if not is_downgrade else downgrade
    handler(db_path.as_posix(), CHANGES_DIRPATH.as_posix(), version)


@contextmanager
def db_session(
    db_path: Path,
    autocommit: bool = True,
) -> Generator[Commands, None, None]:
    """A context manager for a sqlite connection.

    Args:
        db_path (Path):
            The filepath to the database to generate a connection for.
        autocommit (bool, optional):
            If True, commit changes on context manager exit. Defaults to True.

    Yields:
        Commands: A pydapper commands instance.
    """

    connection = sqlite3.connect(db_path.as_posix())
    try:
        yield using(cast(ConnectionType, connection))
        if autocommit:
            connection.commit()
    finally:
        connection.close()


def iter_unprocessed_artifacts(commands: Commands) -> Iterator[Artifact]:
    """Iterate over artifacts that have not been marked as processed.

    Args:
        commands (Commands): The commands session to use for querying.

    Yields:
        Artifact: An artifact that has not been marked as processed.
    """

    query = Query.from_(T_ARTIFACT).select(T_ARTIFACT.star).where(T_ARTIFACT.processed_at.isnull())
    yield from commands.query(str(query), model=Artifact, buffered=True)


def iter_unfetched_artifacts(commands: Commands) -> Iterator[Artifact]:
    """Iterate over artifacts that have not been marked as fetched.

    Args:
        commands (Commands): The commands session to use for querying.

    Yields:
        Artifact: An artifact that has not been marked as fetched.
    """

    query = Query.from_(T_ARTIFACT).select(T_ARTIFACT.star).where(T_ARTIFACT.fetched_at.isnull())
    yield from commands.query(str(query), model=Artifact, buffered=True)


def get_artifact(commands: Commands, fingerprint: str) -> Artifact | None:
    """Get an artifact by its fingerprint.

    Args:
        commands (Commands): The commands session to use for querying.
        fingerprint (str): The artifact fingerprint to get.

    Returns:
        Artifact | None: The artifact with the matching fingerprint if discovered, otherwise None.
    """

    query = (
        Query.from_(T_ARTIFACT).select(T_ARTIFACT.star).where(T_ARTIFACT.fingerprint == fingerprint)
    )

    return commands.query_first_or_default(str(query), model=Artifact, default=None)


def artifact_exists(commands: Commands, fingerprint: str) -> bool:
    """Check if an artifact with a given fingerprint exists.

    Args:
        commands (Commands): The commands session to use for querying.
        fingerprint (str): The artifact fingerprint to check if it exists.

    Returns:
        bool: True if the artifact exists, otherwise False.
    """

    query = Query.from_(T_ARTIFACT).select("1").where(T_ARTIFACT.fingerprint == fingerprint)
    with suppress(NoResultException):
        return commands.execute_scalar(str(query)) is not None

    return False


def create_artifact(commands: Commands, url: str) -> Artifact:
    """Create an artifact from the given URL.

    Args:
        commands (Commands): The commands session to use for querying.
        url (str): The URL to use for the artifact.

    Returns:
        Artifact: The created artifact.
    """

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
    """Ensure that an artifact using the given URL exists.

    Args:
        commands (Commands): The commands session to use for the artifact.
        url (str): The URL of the artifact to ensure.

    Returns:
        Artifact: The artifact that exists or was created in the database.
    """

    artifact = get_artifact(commands, Artifact.build_fingerprint(url))
    if artifact is not None:
        return artifact

    return create_artifact(commands, url)


def mark_artifact_processed(
    commands: Commands,
    artifact: Artifact,
    processed_message: str,
) -> Artifact:
    """Mark an artifact as processed.

    Args:
        commands (Commands): The commands session to use for querying.
        artifact (Artifact): The artifact to mark as processed.
        processed_message (str): The message regarding the processed state.

    Returns:
        Artifact: The artifact marked as processed.
    """

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
    """Mark an artifact as fetched.

    Args:
        commands (Commands): The commands session to use for querying.
        artifact (Artifact): The artifact to mark as fetched.
        fetched_message (str): The message regarding the fetched state.

    Returns:
        Artifact: The artifact marked as fetched.
    """

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
