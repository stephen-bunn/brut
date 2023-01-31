from brut.config import BrutConfig, get_config
from brut.env import get_env
from brut.log import get_logger
from brut.schedule import get_scheduler

env = get_env()
log = get_logger()


def run_app(brut_config: BrutConfig):
    scheduler = get_scheduler(brut_config)
    try:
        log.info("Starting task scheduler")
        scheduler.start()
    finally:
        log.info("Shutting down task scheduler")
        scheduler.shutdown()


if __name__ == "__main__":
    run_app(get_config())
