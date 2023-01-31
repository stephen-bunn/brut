from itertools import groupby
from typing import Type

from brut.types import WatcherProtocol
from brut.watcher.reddit import RedditWatcher

ALL_WATCHERS = [RedditWatcher]


def get_watcher(type: str) -> Type[WatcherProtocol] | None:
    for watcher_type, watcher_iterator in groupby(ALL_WATCHERS, key=lambda watcher: watcher.type):
        if watcher_type != type:
            continue

        return next(watcher_iterator)

    return None
