"""Defines functions to get watchers."""

from itertools import groupby

from brut.types import WatcherProtocol
from brut.watcher.reddit import RedditWatcher

ALL_WATCHERS = [RedditWatcher]
"""A list of all supported watcher classes."""


def get_watcher(type: str) -> WatcherProtocol | None:
    """Get the first watcher matching the provided watcher type.

    Args:
        type (str): The watcher type to get.

    Returns:
        WatcherProtocol | None: The watcher instance if one exists, otherwise None.
    """

    for watcher_type, watcher_iterator in groupby(ALL_WATCHERS, key=lambda watcher: watcher.type):
        if watcher_type != type:
            continue

        return next(watcher_iterator)()

    return None
