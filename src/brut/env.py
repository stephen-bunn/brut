# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains environment variable configuration."""

import os
from pathlib import Path

import environ


@environ.config(prefix="DB")
class DbConfig:
    """Describes environment configuration for the primary database."""

    url: str = environ.var()


@environ.config(prefix="LOG")
class LogConfig:
    """Describes environment configuration for logging."""

    dir: str = environ.var()
    level: str = environ.var(default="DEBUG")
    rotation: str = environ.var(default="00:00")
    retention: str = environ.var(default="10 days")
    compression: str = environ.var(default="zip")
    serialize: bool = environ.bool_var(default=True)
    record: bool = environ.bool_var(default=True)
    debug: bool = environ.bool_var(default=False)


@environ.config(prefix="REDIS")
class RedisConfig:
    """Describes environment configuration for redis."""

    url: str = environ.var("redis://redis:6379/0")


@environ.config(prefix="REDDIT")
class RedditConfig:

    client_id: str = environ.var()
    client_secret: str = environ.var()
    user_agent: str = environ.var()


@environ.config(prefix="APP")
class AppConfig:
    """Describes application environment configuration."""

    db: DbConfig = environ.group(DbConfig)
    log: LogConfig = environ.group(LogConfig)
    redis: RedisConfig = environ.group(RedisConfig)
    reddit: RedditConfig = environ.group(RedditConfig)
    config_path: Path = environ.var(converter=Path)


def get_env() -> AppConfig:
    """Get the current environment instance.

    Returns:
        AppConfig:
            The current environment as read in by the :class:`~AppConfig`.
    """

    return environ.to_config(AppConfig, environ=os.environ)


instance = get_env()
