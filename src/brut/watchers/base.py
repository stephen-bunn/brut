# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains abstractions for other watchers."""

import abc
from typing import Generator

from ..db import Content


class BaseWatcher(abc.ABC):
    """The abstract base watcher class that concrete watcher classes should extend."""

    @abc.abstractproperty
    def type(self) -> str:
        """Type of the watcher.

        This is used for filtering what watcher to use for scheduling based on the
        configuration provided by the config file.

        Raises:
            NotImplementedError:
                Subclasses must override this property.

        Returns:
            str:
                The type of the watcher.
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def iter_content(self, *args, **kwargs) -> Generator[Content, None, None]:
        """Iterate over the available content from this watcher.

        You will likely need to ignore the type signature of this method as it
        is completely defined by the concrete implementation of the watcher.

        Raises:
            NotImplementedError:
                Subclasses must override this method.

        Yields:
            ~brut.db.Content: The discovered content from the watcher.
        """

        raise NotImplementedError()
