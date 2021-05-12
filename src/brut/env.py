# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains environment variable configuration."""

import os
from pathlib import Path

import environ


@environ.config(prefix="APP")
class AppEnv:
    """Describes application environment configuration."""

    config_path: Path = environ.var(converter=Path)


def get_env() -> AppEnv:
    """Get the current environment instance.

    Returns:
        AppConfig:
            The current environment as read in by the :class:`~AppConfig`.
    """

    return environ.to_config(AppEnv, environ=os.environ)


instance = get_env()
