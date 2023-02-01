"""The main thread application that runs a blocking scheduler."""

from brut.config import BrutConfig, get_config
from brut.log import get_logger
from brut.schedule import get_scheduler

log = get_logger()


def run_app(brut_config: BrutConfig):
    """Run the application scheduler given the loaded configuration.

    Args:
        brut_config (BrutConfig): The loaded and validated configuration.
    """

    scheduler = get_scheduler(brut_config)
    try:
        log.info("Starting task scheduler")
        scheduler.start()
    finally:
        log.info("Shutting down task scheduler")
        scheduler.shutdown()


if __name__ == "__main__":
    run_app(get_config())
