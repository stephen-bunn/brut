import json
from pathlib import Path
from typing import Any, TypedDict

import jsonschema
import yaml

from brut.env import instance as env

JSONSCHEMA_FILEPATH = Path(__file__).parent.joinpath("config.schema.json")


class ScheduleConfig(TypedDict):
    crontab: str
    immediate: bool


class WatchConfig(TypedDict):
    name: str
    type: str
    schedule: ScheduleConfig
    args: list[str]
    kwargs: dict[str, Any]


class RedditConfig(TypedDict):
    client_id: str
    client_secret: str
    user_agent: str


class WatcherConfig(TypedDict):
    reddit: RedditConfig


class BrutConfig(TypedDict):
    watchers: WatcherConfig
    watch: list[WatchConfig]
    enqueue: ScheduleConfig


def get_config(config_filepath: Path | None = None) -> BrutConfig:
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
