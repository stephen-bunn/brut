# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains definitions to read in the configuration format."""

from pathlib import Path
from typing import Any, Dict, List

from file_config import config, var

from .env import instance as env


@config
class IntervalConfig:
    """Describes a time interval for a IntervalScheduler."""

    weeks: int = var(required=False)
    days: int = var(required=False)
    hours: int = var(required=False)
    minutes: int = var(required=False)
    seconds: int = var(required=False)


@config
class ScheduleConfig:
    """Describes available schedules for an observe entry."""

    cron: str = var(required=False)
    interval: IntervalConfig = var(required=False)


@config
class ObserveConfig:
    """Describes some content to observe."""

    name: str = var()
    type: str = var()
    args: List[str] = var(required=False)
    kwargs: Dict[str, Any] = var(required=False)
    schedule: ScheduleConfig = var()


@config
class BrutConfig:
    """Contains observe configuration for the app."""

    observe: List[ObserveConfig] = var()


def get_config(config_path: Path) -> BrutConfig:
    """Get the parsed configuration from a given config path.

    Args:
        config_path (~pathlib.Path):
            The path instance to the config file.

    Raises:
        FileNotFoundError:
            If the given config path is not a file.

    Returns:
        BrutConfig:
            The parsed configuration to use within the app.
    """

    if not config_path.is_file():
        raise FileNotFoundError(f"no such file {config_path!s} exists")

    with config_path.open("r") as fp:
        return BrutConfig.load_yaml(fp)  # type: ignore


instance = get_config(env.config_path)
