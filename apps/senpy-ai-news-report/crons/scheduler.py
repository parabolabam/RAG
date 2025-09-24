"""Central APScheduler orchestration for GitHub trends and feeds jobs."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
from contextlib import suppress
from typing import Any, Dict, List

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import STATE_PAUSED, STATE_RUNNING, STATE_STOPPED
from apscheduler.triggers.cron import CronTrigger

from crons.feeds_cron import main as feeds_job
from crons.github_trends_cron import main as github_job

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DEFAULT_TRENDS_CRON = "0 5 * * *"  # every day at 05:00 UTC
DEFAULT_FEEDS_CRON = "0 8 * * *"  # every day at 08:00 UTC

KNOWN_JOB_IDS = ("github_trends", "feeds_parser")

_scheduler_lock = asyncio.Lock()
_scheduler: AsyncIOScheduler | None = None


class SchedulerNotRunningError(RuntimeError):
    """Raised when an operation requires the scheduler to be running."""


class UnknownJobError(KeyError):
    """Raised when the requested job id is not registered."""


async def run_github_job() -> None:
    logger.info("GitHub trends job starting")
    await github_job()
    logger.info("GitHub trends job finished")


async def run_feeds_job() -> None:
    logger.info("Feeds job starting")
    await feeds_job()
    logger.info("Feeds job finished")


_JOB_HANDLERS = {
    "github_trends": run_github_job,
    "feeds_parser": run_feeds_job,
}


def _cron_expression(env_var: str, default: str) -> str:
    value = os.getenv(env_var)
    if not value or not value.strip():
        return default
    return value.strip()


def _build_cron_trigger(expression: str, fallback: str, timezone: str, job_name: str) -> CronTrigger:
    try:
        return CronTrigger.from_crontab(expression, timezone=timezone)
    except ValueError as exc:
        logger.warning(
            "Invalid cron expression '%s' for %s (%s). Falling back to '%s'",
            expression,
            job_name,
            exc,
            fallback,
        )
        return CronTrigger.from_crontab(fallback, timezone=timezone)


def _schedule_jobs(
    scheduler: AsyncIOScheduler,
    timezone: str,
    trends_cron: str,
    feeds_cron: str,
) -> None:
    scheduler.add_job(
        run_github_job,
        _build_cron_trigger(trends_cron, DEFAULT_TRENDS_CRON, timezone, "github_trends"),
        id="github_trends",
        name="GitHub Trends",
        replace_existing=True,
        coalesce=True,
    )
    scheduler.add_job(
        run_feeds_job,
        _build_cron_trigger(feeds_cron, DEFAULT_FEEDS_CRON, timezone, "feeds_parser"),
        id="feeds_parser",
        name="Feeds Parser",
        replace_existing=True,
        coalesce=True,
    )


async def ensure_scheduler_started(refresh: bool = False) -> AsyncIOScheduler:
    """Ensure the scheduler is configured and running.

    Args:
        refresh: Reload cron expressions from the environment even if already running.
    """

    async with _scheduler_lock:
        global _scheduler

        timezone = os.getenv("CRON_TIMEZONE", "UTC")
        trends_cron = _cron_expression("GITHUB_TRENDS_CRON", DEFAULT_TRENDS_CRON)
        feeds_cron = _cron_expression("FEEDS_PARSER_CRON", DEFAULT_FEEDS_CRON)

        scheduler = _scheduler
        if scheduler is None:
            scheduler = AsyncIOScheduler(timezone=timezone)
            _schedule_jobs(scheduler, timezone, trends_cron, feeds_cron)
            scheduler.start()
            _scheduler = scheduler
            logger.info(
                "Scheduler initialized (timezone=%s, github_cron='%s', feeds_cron='%s')",
                timezone,
                trends_cron,
                feeds_cron,
            )
        else:
            scheduler.configure(timezone=timezone)
            if refresh or scheduler.get_job("github_trends") is None or scheduler.get_job("feeds_parser") is None:
                _schedule_jobs(scheduler, timezone, trends_cron, feeds_cron)
            if scheduler.state == STATE_STOPPED:
                scheduler.start()
            logger.info(
                "Scheduler refreshed (timezone=%s, github_cron='%s', feeds_cron='%s')",
                timezone,
                trends_cron,
                feeds_cron,
            )

        return scheduler


def _require_scheduler_running() -> AsyncIOScheduler:
    scheduler = _scheduler
    if scheduler is None or scheduler.state == STATE_STOPPED:
        raise SchedulerNotRunningError("Scheduler is not running")
    return scheduler


async def shutdown_scheduler(wait: bool = False) -> None:
    async with _scheduler_lock:
        global _scheduler
        if _scheduler and _scheduler.state != STATE_STOPPED:
            _scheduler.shutdown(wait=wait)
            logger.info("Scheduler shut down (wait=%s)", wait)
        _scheduler = None


def pause_job(job_id: str) -> None:
    scheduler = _require_scheduler_running()
    try:
        scheduler.pause_job(job_id)
        logger.info("Paused job '%s'", job_id)
    except JobLookupError as exc:
        raise UnknownJobError(job_id) from exc


def resume_job(job_id: str) -> None:
    scheduler = _require_scheduler_running()
    try:
        scheduler.resume_job(job_id)
        logger.info("Resumed job '%s'", job_id)
    except JobLookupError as exc:
        raise UnknownJobError(job_id) from exc


async def trigger_job(job_id: str) -> None:
    try:
        handler = _JOB_HANDLERS[job_id]
    except KeyError as exc:
        raise UnknownJobError(job_id) from exc

    logger.info("Manual trigger for job '%s'", job_id)
    await handler()


def get_scheduler_state() -> str:
    scheduler = _scheduler
    if scheduler is None:
        return "not_started"
    mapping = {
        STATE_RUNNING: "running",
        STATE_PAUSED: "paused",
        STATE_STOPPED: "stopped",
    }
    return mapping.get(scheduler.state, "unknown")


def get_jobs_overview() -> List[Dict[str, Any]]:
    scheduler = _scheduler
    if scheduler is None:
        return []

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "paused": job.next_run_time is None,
            }
        )
    return jobs


async def run_forever() -> None:
    await ensure_scheduler_started(refresh=True)

    stop_event = asyncio.Event()

    def _stop() -> None:
        if not stop_event.is_set():
            logger.info("Stopping scheduler (signal received)")
            stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, _stop)

    try:
        await stop_event.wait()
    finally:
        await shutdown_scheduler(wait=True)


__all__ = [
    "KNOWN_JOB_IDS",
    "ensure_scheduler_started",
    "shutdown_scheduler",
    "pause_job",
    "resume_job",
    "trigger_job",
    "get_scheduler_state",
    "get_jobs_overview",
    "run_forever",
    "SchedulerNotRunningError",
    "UnknownJobError",
]
