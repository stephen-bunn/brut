# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains module-wide helpers."""

from .config import instance as config
from .log import DEFAULT_LOG_DIRPATH, configure_logger
from .log import instance as log


def setup_logging():
    """Configure logging based on the current environment configuration."""

    if not DEFAULT_LOG_DIRPATH.is_dir() and config.log.record:
        DEFAULT_LOG_DIRPATH.mkdir(parents=True)

    configure_logger(
        log,
        level=config.log.level,
        record=config.log.record,
        debug=config.log.debug,
    )
