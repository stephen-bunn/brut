"""Defines application logging helpers."""

import sys

import loguru
from logging_loki import LokiHandler

from brut.constants import APP_NAME, APP_VERSION
from brut.env import instance as env


def configure_logger(
    logger: "loguru.Logger",
    level: str = "INFO",
) -> "loguru.Logger":
    """Configure the provided logger instance.

    Args:
        logger (loguru.Logger):
            The logger to configure.
        level (str, optional):
            The logging level to use for the stdout logger.
            Defaults to "INFO".

    Returns:
        loguru.Logger: The configured logger instance.
    """

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


def get_logger() -> "loguru.Logger":
    """Get the logging logger to use for the requesting module.

    Returns:
        loguru.Logger: The logger instance to use for the requesting module.
    """

    return configure_logger(loguru.logger, level=env.log.level)
