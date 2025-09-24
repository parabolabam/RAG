import asyncio
import logging

from crons.scheduler import run_forever

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


if __name__ == "__main__":
    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Cron scheduler interrupted by user")
