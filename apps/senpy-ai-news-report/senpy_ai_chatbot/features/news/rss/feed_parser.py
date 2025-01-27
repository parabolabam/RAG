import asyncio
import feedparser
from datetime import datetime
import time

from telethon.client.downloads import aiohttp

from senpy_ai_chatbot.features.ai.openai_client import AiNewsClient
from senpy_ai_chatbot.features.news.rss.rss_feeds import RSS_FEEDS
from senpy_ai_chatbot.features.telegram_integration_features.send_channel_message import (
    send_message_to_channel,
)
from .rss_prompts import rss_system_promt, rss_user_promt


async def process_rss_with_ai(rss_entries):

    return await AiNewsClient().process_news(
        system_prompt=rss_system_promt,
        user_prompt=rss_user_promt,
        data=rss_entries,
    )


async def fetch_feed(session, url):
    """Fetch a single RSS feed asynchronously."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                feed_data = await response.text()
                return url, feedparser.parse(feed_data)
            else:
                print(f"Failed to fetch {url} (status: {response.status})")
                return url, None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return url, None


async def fetch_all_feeds(urls):
    """Fetch all RSS feeds concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def check_feed_updated(feed, last_run_date):
    """Check if the feed was updated since the calculated last run date."""

    if "updated_parsed" in feed and feed.feed.updated_parsed:
        feed_updated_date = datetime.fromtimestamp(
            time.mktime(feed.feed.updated_parsed)
        )
        return feed_updated_date > last_run_date, feed_updated_date
    return False, None


async def parse_feeds():
    """Main function to process multiple feeds asynchronously."""

    # Fetch all feeds asynchronously
    feed_results = await fetch_all_feeds(RSS_FEEDS)
    processes_results = []
    for idx, feed_entry in enumerate(feed_results):
        print(idx)
        ai_proccessed_result = await process_rss_with_ai(feed_entry)

        (
            await send_message_to_channel(
                ai_proccessed_result.choices[0].message.content or "",
            )
            if ai_proccessed_result.choices[0].message.content != ""
            else ""
        )
        processes_results.append(ai_proccessed_result)

    return processes_results
