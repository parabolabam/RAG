import asyncio
import feedparser
from datetime import datetime
import time
import logging
import os

from telethon.client.downloads import aiohttp

from senpy_ai_news_report.features.ai.openai_client import AiNewsClient
from senpy_ai_news_report.features.news.rss.rss_feeds import RSS_FEEDS
from senpy_ai_news_report.features.telegram_integration_features.send_channel_message import (
    send_message_to_channel,
)
from .rss_prompts import rss_system_promt, rss_user_promt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def process_rss_with_ai(rss_entries, model: str | None = None):
    if model is None:
        model = "gpt-4o-mini"
    logging.info(f"Processing RSS entries with AI model: {model}")
    return await AiNewsClient().process_news(
        system_prompt=rss_system_promt,
        user_prompt=rss_user_promt,
        data=rss_entries,
        model=model,
    )


async def process_rss_with_ai_in_batch(rss_entries, model: str | None = None):
    if model is None:
        model = "gpt-4o-mini"

    return await AiNewsClient().process_news_in_batch(
        system_prompt=rss_system_promt,
        user_prompt=rss_user_promt,
        data_list=rss_entries,
        model=model,
    )


async def process_rss_with_ai_batch(
    rss_entries_list, model: str | None = None, use_openai_batch_api: bool = False
):
    """
    Process multiple RSS entries using batch processing.

    Args:
        rss_entries_list: List of RSS entry data
        model: OpenAI model to use
        use_openai_batch_api: Whether to use OpenAI Batch API (slower but cheaper) or concurrent processing
    """
    if model is None:
        model = "gpt-4o-mini"

    ai_client = AiNewsClient()

    # Use OpenAI Batch API for cost efficiency (slower but cheaper)
    return await ai_client.process_news_in_batch(
        system_prompt=rss_system_promt,
        user_prompt=rss_user_promt,
        data_list=rss_entries_list,
        model=model,
    )


async def fetch_feed(session, url):
    """Fetch a single RSS feed asynchronously."""
    logging.info(f"Fetching feed from {url}")
    try:
        async with session.get(url) as response:
            if response.status == 200:
                feed_data = await response.text()
                logging.info(f"Successfully fetched feed from {url}")
                return url, feedparser.parse(feed_data)
            else:
                logging.error(f"Failed to fetch {url} (status: {response.status})")
                return url, None
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return url, None


async def fetch_all_feeds(urls):
    """Fetch all RSS feeds concurrently."""
    logging.info("Fetching all RSS feeds.")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    logging.info("Finished fetching all RSS feeds.")
    return results


def check_feed_updated(feed, last_run_date):
    """Check if the feed was updated since the calculated last run date."""
    if "updated_parsed" in feed and feed.feed.updated_parsed:
        feed_updated_date = datetime.fromtimestamp(
            time.mktime(feed.feed.updated_parsed)
        )
        is_updated = feed_updated_date > last_run_date
        logging.info(
            f"Feed updated status: {is_updated} for feed updated at {feed_updated_date}"
        )
        return is_updated, feed_updated_date
    logging.info("Feed does not have 'updated_parsed' field.")
    return False, None


async def parse_feeds():

    # Fetch all feeds asynchronously
    feed_results = await fetch_all_feeds(RSS_FEEDS)
    # print(feed_results[:1][0])

    # Extract data from feed results
    feed_data_list = []
    for feed_entry in feed_results[:1]:  # Process first feed for now
        url, data = feed_entry
        if data:  # Make sure data is not None
            print(data.entries[:5])
            feed_data_list.append(
                data.entries[:5]
            )  # Limit to first 5 entries for batch processing

    if feed_data_list:
        # Process all feeds in batch
        batch_results = await process_rss_with_ai_in_batch(
            feed_data_list,
            model="gpt-4.1",
        )
        return batch_results
    else:
        print("No valid feed data to process")
        return []


async def post_feeds(
    feed_results,
):
    """
    Main function to process multiple feeds asynchronously and send to Telegram.

    Args:
        telegram_channel_id: Telegram channel ID to send messages to
    """

    for result in feed_results:
        response = result["response"]
        body = response["body"]
        choices = body["choices"][0]
        content = choices["message"]["content"]
        if content is not None:
            await send_message_to_channel(message=content, telegram_channel_id=None)

    return feed_results
