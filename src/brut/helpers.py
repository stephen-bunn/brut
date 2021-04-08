# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""
"""

from .env import instance as env
from .log import configure_logger
from .log import instance as log


def setup_logging():
    configure_logger(
        log,
        level=env.log.level,
        record=env.log.record,
        debug=env.log.debug,
    )
