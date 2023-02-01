"""Defines types used in the library."""

from typing import ClassVar, Iterator, Protocol

from brut.db.models import Artifact


class WatcherProtocol(Protocol):
    """The protocol to inherit for watchers."""

    type: ClassVar[str]
    """The unique type of the watcher."""

    def iter_artifacts(self, *args, **kwargs) -> Iterator[Artifact]:
        """Iterate over artifacts discovered from the watcher.

        Yields:
            Artifact: The discovered artifact.
        """

        ...
