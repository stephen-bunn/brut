from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from uuid import UUID

from megu.hash import HashType, hash_io
from url_normalize import url_normalize


@dataclass
class Artifact:
    id: UUID = field()
    created_at: datetime = field()
    fingerprint: str = field()
    url: str = field()
    fetched_at: datetime | None = field(default=None)
    fetched_message: str | None = field(default=None)
    processed_at: datetime | None = field(default=None)
    processed_message: str | None = field(default=None)

    @staticmethod
    def build_fingerprint(url: str) -> str:
        return hash_io(
            BytesIO(bytes(url_normalize(url), "utf-8")),
            {HashType.SHA256},
        )[HashType.SHA256]
