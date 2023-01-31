from typing import ClassVar, Iterator, Protocol

from brut.db.models import Artifact


class WatcherProtocol(Protocol):
    type: ClassVar[str]

    def iter_artifacts(self, *args, **kwargs) -> Iterator[Artifact]:
        ...
