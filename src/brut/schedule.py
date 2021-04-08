# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains functions for building the appropriate tasks scheduler."""

from functools import partial
from typing import Optional, Union

import file_config
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .config import BrutConfig, ScheduleConfig
from .log import instance as log
from .tasks import handle_content


def get_trigger(
    schedule: ScheduleConfig,
) -> Optional[Union[IntervalTrigger, CronTrigger]]:
    """Get the appropriate APScheduler trigger for a given ScheduleConfig.

    Args:
        schedule (~brut.config.ScheduleConfig):
            The config to interpret as an APScheduler trigger.

    Returns:
        Optional[Union[
            ~apscheduler.triggers.interval.IntervalTrigger,
            ~apscheduler.triggers.cron.CronTrigger
        ]]:
            The APScheduler trigger if determined.
    """

    if schedule.cron is not None:
        return CronTrigger.from_crontab(schedule.cron)
    elif schedule.interval is not None:
        return IntervalTrigger(**file_config.to_dict(schedule.interval))

    return None


def schedule_listener(event):
    if event.exception:
        log.error(
            "Unexpected exception occurred during task scheduling job "
            f"{event.job_id!r}",
            event.exception,
        )
    else:
        log.debug(f"Scheduler successfully kicked off job {event.job_id!r}")


def get_scheduler(config: BrutConfig) -> BlockingScheduler:
    """Build the blocking scheduler for the given BrutConfig.

    Parameters:
        config (~brut.config.BrutConfig):
            The current Brut configuration.

    Returns:
        ~apscheduler.schedulers.blocking.BlockingScheduler:
            The scheduler to use for running the configured Brut tasks.
    """

    log.info(f"Constructing a blocking scheduler based on configuration from {config}")
    scheduler = BlockingScheduler()

    for observe in config.observe:
        trigger = get_trigger(observe.schedule)
        if not trigger:
            log.warning(
                f"Trigger could not be determined for {observe.schedule}, "
                f"skipping adding {observe.name!r}"
            )

        args = observe.args or []
        kwargs = observe.kwargs or {}
        log.info(f"Adding job {observe.name!r} using trigger {trigger}")

        job = partial(
            handle_content.send,
            observe.type,
            *args,
            **kwargs,
        )

        scheduler.add_job(job, trigger=trigger)

    scheduler.add_listener(schedule_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    return scheduler
