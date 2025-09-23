import logging
import asyncio
from senpy_ai_news_report.features.news.rss.feed_parser import post_feeds, parse_feeds

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    logging.info("Starting 'post_feeds' job.")
    try:
        feeds = await parse_feeds()
        await post_feeds(feeds)
        logging.info("'post_feeds' job finished successfully.")
    except Exception as e:
        logging.error(f"'post_feeds' job failed: {e}")
        raise

if __name__ == "__main__":
    logging.info("Running feeds cron script.")
    asyncio.run(main())
