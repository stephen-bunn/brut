"""Defines required environment variables for the running application."""

from pathlib import Path

from environ import config, group, to_config, var


@config(prefix="LOG")
class LogEnv:
    """Brut logging environment variables."""

    level: str = var(default="INFO")
    """The logging level to log to stdout."""

    loki_url: str | None = var(default=None)
    """The Loki URL to send log records to."""


@config(prefix="MEGU")
class MeguEnv:
    """Brut-specific Megu environment variables."""

    plugin_dir: Path = var(converter=Path)
    """The plugin directory to store and load Megu plugins from."""


@config(prefix="REDDIT")
class RedditEnv:
    """Brut Reddit client environment variables."""

    client_id: str = var()
    """Reddit client ID."""

    client_secret: str = var()
    """Reddit client secret."""

    user_agent: str = var()
    """The User-Agent header value to use for the Reddit client."""


@config(prefix="BRUT")
class BrutEnv:
    """Brut environment variables."""

    database_path: Path = var(converter=Path)
    """The filepath the Brut database lives at."""

    redis_url: str = var()
    """The Redis URL to use for the Brut task broker."""

    config_path: Path = var(converter=Path)
    """The filepath the Brut configuration lives at."""

    store_dir: Path = var(converter=Path)
    """The directory path that fetched Brut artifacts should be stored at."""

    log: LogEnv = group(LogEnv)
    """Brut logging environment variables."""

    megu: MeguEnv = group(MeguEnv)
    """Brut-specific Megu environment variables."""

    reddit: RedditEnv = group(RedditEnv)
    """Brut Reddit client environment variables."""


def get_env() -> BrutEnv:
    """Get required environment variables.

    Returns:
        BrutEnv: The required environment variables.
    """

    return to_config(BrutEnv)


instance = get_env()
"""The import-loaded required environment variables."""
