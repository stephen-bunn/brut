# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the core bootstrap methods for the application."""

from .config import instance as config
from .helpers import setup_logging
from .log import instance as log
from .schedule import get_scheduler

# brut.app is an entrypoint for the app, ensure logging is setup early
setup_logging()


def run_app():
    """Bootstrap and run the application scheduler."""

    scheduler = get_scheduler(config)
    try:
        log.info("Starting up task scheduler")
        scheduler.start()
    finally:
        log.info("Shutting down task scheduler")
        scheduler.shutdown()


# allow triggering this application through `python -m brut.app`
if __name__ == "__main__":
    run_app()
