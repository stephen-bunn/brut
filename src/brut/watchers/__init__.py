# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains watchers and helper methods to get desired watchers."""

from itertools import groupby
from typing import Optional, Type

from ..log import instance as log
from .base import BaseWatcher
from .reddit import SubredditWatcher

ALL_WATCHERS = [SubredditWatcher]


def get_watcher(type: str) -> Optional[Type[BaseWatcher]]:
    """Get the best watcher for the given watcher type.

    Args:
        type (str):
            The watcher type to find.

    Returns:
        Optional[Type[BaseWatcher]]:
            The class of the desired watcher, if discovered.
    """

    type = type.lower()
    for watcher_type, watcher_iterator in groupby(ALL_WATCHERS, key=lambda w: w.type):
        if watcher_type.lower() != type:
            continue
        else:
            watchers = list(watcher_iterator)
            if len(watchers) > 1:
                log.warning(
                    f"Watcher type {type!r} has many matches {watchers!r}, "
                    "using the first one"
                )

            return watchers[0]

    return None


__all__ = ["SubredditWatcher"]
