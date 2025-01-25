# Start the scheduler to send news summaries daily
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class CronConfig:
    hour: int
    minute: int


def launch_scheduler(cron_config: CronConfig) -> AsyncIOScheduler:
    """
    Launches an AsyncIO scheduler and schedules the news summary job.

    Args:
        cron_config (CronConfig): Configuration object containing the hour for the cron job.

    Returns:
        AsyncIOScheduler: The initialized and configured scheduler instance.
    """

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        None,
        "cron",
        {"hour": cron_config.hour, "minute": cron_config.minute},
    )  # Adjust the time as needed

    return scheduler
