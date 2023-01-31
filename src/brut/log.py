import sys
from functools import lru_cache
from logging import Logger

import loguru


def configure_logger(
    logger: Logger,
    level: str = "INFO",
) -> Logger:
    logger.configure(  # type: ignore
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
    return logger


@lru_cache
def get_logger() -> Logger:
    return configure_logger(loguru.logger)  # type: ignore
