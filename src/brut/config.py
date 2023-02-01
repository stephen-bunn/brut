"""Contains data definitions and functions to load task configuration."""

import json
from pathlib import Path
from typing import Any, TypedDict

import jsonschema
import yaml

from brut.env import instance as env

JSONSCHEMA_FILEPATH = Path(__file__).parent.joinpath("config.schema.json")
"""The filepath to the library-bundled JSONSchema document for task configuration."""


class ScheduleConfig(TypedDict):
    """Defines a schedule for a task to follow."""

    crontab: str
    """Crontab definition for the scheduler to use."""

    immediate: bool
    """If true, the task following this schedule is triggered immediately."""


class WatchConfig(TypedDict):
    """Defines a task to watch for content."""

    name: str
    """The name of the watch configuration, should be unique."""

    type: str
    """The type of the watcher to use for this task.
    This should map to one of the library-included :class:`~brut.types.WatcherProtocol` subclases.
    """

    schedule: ScheduleConfig
    """The schedule this watch task should follow."""

    args: list[str]
    """Positional arguments to pass through to the watcher type."""

    kwargs: dict[str, Any]
    """Keyword arguments to pass through to the watcher type."""


class BrutConfig(TypedDict):
    """Defines task configuration for the library."""

    watch: list[WatchConfig]
    """A list of watch task configurations."""

    enqueue: ScheduleConfig
    """The schedule that new artifacts should be enqueued for fetching."""


def get_config(config_filepath: Path | None = None) -> BrutConfig:
    """Read, parse, and validate the library configuration.

    Args:
        config_filepath (Path | None, optional):
            The filepath to the library configuration.
            Defaults to None.

    Raises:
        FileNotFoundError: If the provided config filepath does not exist

    Returns:
        BrutConfig: The loaded and validated configuration.
    """

    if config_filepath is None:
        config_filepath = env.config_path

    if not config_filepath.is_file():
        raise FileNotFoundError(f"No file exists at {config_filepath}")

    with JSONSCHEMA_FILEPATH.open("r") as schema_io:
        schema = json.load(schema_io)

    with config_filepath.open("r") as config_io:
        config_data = yaml.load(config_io, yaml.Loader)
        jsonschema.validate(config_data, schema)
        return config_data
