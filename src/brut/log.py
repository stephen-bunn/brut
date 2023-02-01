import sys
from functools import lru_cache

import loguru
from logging_loki import LokiHandler

from brut.constants import APP_NAME, APP_VERSION
from brut.env import instance as env


def configure_logger(
    logger: "loguru.Logger",
    level: str = "INFO",
) -> "loguru.Logger":
    logger.configure(
        handlers=[
            dict(
                sink=sys.stdout,
                level=level,
                format="[{time}] [PID {process}] [{name}] [{level}] {message}",
                diagnose=level.upper() == "DEBUG",
                backtrace=level.upper() == "DEBUG",
            )
        ]
    )

    if env.log.loki_url is not None:
        logger.add(
            sink=LokiHandler(
                url=env.log.loki_url,
                tags={"app": APP_NAME, "version": APP_VERSION},
                version="1",
            )
        )

    return logger


@lru_cache
def get_logger() -> "loguru.Logger":
    return configure_logger(loguru.logger, level=env.log.level)  # type: ignore
