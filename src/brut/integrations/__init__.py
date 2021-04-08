# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

from typing import Optional, Type

from .base import BaseIntegration
from .reddit import SubredditIntegration

ALL_INTEGRATIONS = [SubredditIntegration]


def get_integration(type: str) -> Optional[Type[BaseIntegration]]:
    for integration in ALL_INTEGRATIONS:
        if integration.name.lower() == type.lower():
            return integration

    return None


__all__ = ["SubredditIntegration"]
