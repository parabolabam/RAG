import logging
import asyncio
from senpy_ai_news_report.features.news.github_trending.post_github_trends import (
    post_github_trends,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    logging.info("Starting 'post_github_trends' job.")
    try:
        await post_github_trends(None, 5, None)
        logging.info("'post_github_trends' job finished successfully.")
    except Exception as e:
        logging.error(f"'post_github_trends' job failed: {e}")
        raise

if __name__ == "__main__":
    logging.info("Running github trends cron script.")
    asyncio.run(main())
