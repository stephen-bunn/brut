# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains functions for building the appropriate tasks scheduler."""

from functools import partial
from typing import Optional, Union

import file_config
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, SchedulerEvent
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .config import BrutConfig, ScheduleConfig
from .log import instance as log
from .tasks import enqueue, watch


def get_trigger(
    schedule_config: ScheduleConfig,
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

    if schedule_config.crontab is not None:
        return CronTrigger.from_crontab(schedule_config.crontab)
    elif schedule_config.interval is not None:
        return IntervalTrigger(**file_config.to_dict(schedule_config.interval))

    return None


def schedule_listener(event: SchedulerEvent):
    """Schedule listener function responsible for reporting scheduler status.

    Args:
        event (~apscheduler.events.SchedulerEvent):
            The APScheduler event.
    """

    if event.exception:
        log.error(
            "Unexpected exception occurred during task scheduling job "
            f"{event.job_id!r}",
            event.exception,
        )
    else:
        log.debug(f"Scheduler successfully kicked off job {event.job_id!r}")


def get_scheduler(brut_config: BrutConfig) -> BlockingScheduler:
    """Build the blocking scheduler for the given BrutConfig.

    Parameters:
        brut_config (~brut.config.BrutConfig):
            The current Brut configuration.

    Returns:
        ~apscheduler.schedulers.blocking.BlockingScheduler:
            The scheduler to use for running the configured Brut tasks.
    """

    log.info(
        f"Constructing a blocking scheduler based on configuration from {brut_config}"
    )
    scheduler = BlockingScheduler()
    scheduler.add_listener(schedule_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # add watch jobs for polling for new content
    for watch_config in brut_config.watch:
        trigger = get_trigger(watch_config.schedule)
        if not trigger:
            log.warning(
                f"Trigger could not be determined for {watch_config.schedule}, "
                f"skipping adding {watch_config.name!r}"
            )

        args = watch_config.args or []
        kwargs = watch_config.kwargs or {}
        log.info(f"Adding watch job {watch_config.name!r} using trigger {trigger}")

        job = partial(
            watch.send,
            watch_config.type,
            *args,
            **kwargs,
        )

        scheduler.add_job(job, trigger=trigger)
        if watch_config.schedule.immediate:
            log.info(f"Immediately triggering {watch_config.name}")
            job()

    # Add the enqueue job for fetched content
    enqueue_trigger = get_trigger(brut_config.enqueue)
    log.info(f"Adding fetch enqueue job using trigger {enqueue_trigger}")
    scheduler.add_job(enqueue.send, trigger=enqueue_trigger)

    return scheduler
