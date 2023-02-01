"""Defines helpers to create the desired scheduler."""

from functools import partial

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, SchedulerEvent
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from brut.config import BrutConfig, ScheduleConfig
from brut.log import get_logger
from brut.tasks import enqueue, watch

log = get_logger()


def get_trigger(schedule_config: ScheduleConfig) -> CronTrigger:
    """Create a trigger from the provided schedule configuration.

    Args:
        schedule_config (ScheduleConfig): The schedule configuration.

    Returns:
        CronTrigger: The created trigger from the given schedule configuration.
    """

    return CronTrigger.from_crontab(schedule_config["crontab"])


def schedule_listener(event: SchedulerEvent):
    """The listener for the schedule executions.

    Args:
        event (SchedulerEvent): The event being sent from the scheduler.
    """

    if event.exception:  # type: ignore
        log.error(
            f"Unexpected error occured during task {event.job_id}",  # type: ignore
            event.exception,  # type: ignore
        )
    else:
        log.debug(f"Kicked off job {event.job_id}")  # type: ignore


def get_scheduler(brut_config: BrutConfig) -> BlockingScheduler:
    """Build the necessary scheduler given the Brut configuration.

    Args:
        brut_config (BrutConfig): The Brut configuration to build the scheduler from.

    Returns:
        BlockingScheduler: The built blocking scheduler.
    """

    scheduler = BlockingScheduler()
    scheduler.add_listener(schedule_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    for watch_config in brut_config["watch"]:
        args = watch_config.get("args", [])
        kwargs = watch_config.get("kwargs", {})

        log.info(f"Adding watch job {watch_config['name']}")
        job = partial(watch.send, watch_config["type"], *args, **kwargs)
        scheduler.add_job(job, trigger=get_trigger(watch_config["schedule"]))

        if watch_config["schedule"]["immediate"]:
            log.info(f"Immediately triggering watch job {watch_config['name']}")
            job()

    log.info("Adding enqueue job")
    scheduler.add_job(enqueue.send, trigger=get_trigger(brut_config["enqueue"]))
    if brut_config["enqueue"]["immediate"]:
        log.info("Immediately triggering enqueue")
        enqueue()

    return scheduler
