"""Contains database models used throughout the library."""

from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from uuid import UUID

from megu.hash import HashType, hash_io
from url_normalize import url_normalize


@dataclass
class Artifact:
    """Discovered artifacts from watchers."""

    id: UUID = field()
    """The unique ID of the artifact."""

    created_at: datetime = field()
    """The datetime the artifact record was created at."""

    fingerprint: str = field()
    """The unique artifact fingerprint."""

    url: str = field()
    """The artifact URL."""

    fetched_at: datetime | None = field(default=None)
    """The optional datetime when the artifact was fetched."""

    fetched_message: str | None = field(default=None)
    """The optional message describing the status of the artifact fetch."""

    processed_at: datetime | None = field(default=None)
    """The optional datetime when the artifact was processed."""

    processed_message: str | None = field(default=None)
    """The optional message describing the status of the artifact processed."""

    @staticmethod
    def build_fingerprint(url: str) -> str:
        """Build the fingerprint of an artifact given the artifact URL.

        Args:
            url (str): The URL of the artifact to use for the fingerprint.

        Returns:
            str: The fingerprint of the artifact.
        """

        return hash_io(
            BytesIO(bytes(url_normalize(url), "utf-8")),
            {HashType.SHA256},
        )[HashType.SHA256]
