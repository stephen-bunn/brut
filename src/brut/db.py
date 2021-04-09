# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains database models an type definitions."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from typing import Generator, List, Optional

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, registry, relationship

from .env import instance as env
from .hasher import HashType, hash_io
from .log import instance as log

# The SQLAlchemy ORM registry that we use to decorate dataclasses with
orm_registry = registry()


@orm_registry.mapped
@dataclass
class Content:
    """Describes some extracted content."""

    __table__ = Table(
        "content",
        orm_registry.metadata,
        Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
        Column("created_at", DateTime, server_default=func.now()),
        Column("source", String(256)),
        Column("source_id", String(256)),
        Column("fingerprint", String(64), unique=True),
        Column("url", String(2048)),
        Column("data", Text),
        Column("processed_at", DateTime, nullable=True, default=None),
        Column("processed_message", Text, nullable=True, default=None),
    )
    __mapper_args__ = {"properties": {"artifacts": relationship("Artifact")}}

    id: int = field(init=False)
    created_at: datetime
    source: str
    source_id: str
    fingerprint: str
    url: str
    data: str
    processed_at: Optional[datetime] = field(default=None)
    processed_message: Optional[str] = field(default=None)
    artifacts: List[Artifact] = field(default_factory=list)

    @staticmethod
    def build_fingerprint(source: str, source_id: str) -> str:
        """Build the appropriate fingerprint for a given source and source id.

        Args:
            source (str):
                The source that this content is using.
            source_id (str):
                The source_id that this content is using.

        Returns:
            str:
                The appropriate SHA-256 fingerprint for the content.
        """

        fingerprint = hash_io(
            BytesIO(bytes(f"{source!s}|{source_id!s}", "utf-8")),
            {HashType.SHA256},
        )[HashType.SHA256]
        log.debug(
            f"Computed fingerprint for ({source!r}, {source_id!r}) as {fingerprint!r}"
        )

        return fingerprint


@orm_registry.mapped
@dataclass
class Artifact:
    """Describes some downloaded artifact."""

    __table__ = Table(
        "artifact",
        orm_registry.metadata,
        Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
        Column("created_at", DateTime, server_default=func.now()),
        Column("fingerprint", String(64), unique=True),
        Column("content_id", ForeignKey("content.id")),
    )

    id: int = field(init=False)
    created_at: datetime
    fingerprint: str
    content_id: int = field(init=False)


@lru_cache
def get_engine() -> Engine:
    """Get the SQLAlchemy engine with the bound model registry metadata.

    Returns:
        sqlalchemy.engine.Engine:
            The SQLAlchemy engine for the primary database.
    """

    log.info(f"Constructing a database engine from {env.db.url!r}")
    engine = create_engine(env.db.url)
    orm_registry.metadata.bind = engine
    return engine


@contextmanager
def db_session(
    commit: bool = True,
    rollback: bool = True,
    reraise: bool = True,
) -> Generator[Session, None, None]:
    """Get access to the database session as a context manager.

    Args:
        commit (bool, optional):
            Auto commit changes on context leave.
            Defaults to True.
        rollback (bool, optional):
            Auto rollback changes on failures prior to context leave.
            Defaults to True.
        reraise (bool, optional):
            Reraise exceptions encountered during database session.
            Defaults to True.

    Raises:
        Exception:
            Will reraise any exception if `reraise` is truthy.

    Yields:
        ~sqlalchemy.orm.Session:
            The session to use for database interaction.
    """

    with Session(get_engine()) as session:
        with log.contextualize(session_id=hash(session)):
            try:
                log.debug("Opening a database session")
                yield session

                if commit:
                    log.debug("Commiting changes for opened session before close")
                    session.commit()
            except Exception as exc:
                log.exception(f"Unexpected exception occurred during session, {exc}")

                if rollback:
                    log.warning("Rolling back changes for session before close")
                    session.rollback()

                if reraise:
                    raise exc
            finally:
                log.debug("Closing an opened database session")
                session.close()
