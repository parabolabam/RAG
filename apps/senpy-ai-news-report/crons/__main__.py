from senpy_ai_news_report.features.news.github_trending.post_github_trends import (
    post_github_trends,
)
from senpy_ai_news_report.features.news.rss.feed_parser import post_feeds, parse_feeds
import asyncio


async def main():
    await post_github_trends(None, 5, None)
    await post_feeds(await parse_feeds())


if __name__ == "__main__":
    print("Running cron...")
    asyncio.run(main())
