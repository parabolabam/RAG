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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
    logging.info(f"Processing RSS entries in batch with AI model: {model}")
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

    logging.info(f"Processing RSS entries in batch with AI model: {model}, use_openai_batch_api: {use_openai_batch_api}")
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
        logging.info(f"Feed updated status: {is_updated} for feed updated at {feed_updated_date}")
        return is_updated, feed_updated_date
    logging.info("Feed does not have 'updated_parsed' field.")
    return False, None


async def parse_feeds():
    logging.info("Starting to parse feeds.")
    # Fetch all feeds asynchronously
    feed_results = await fetch_all_feeds(RSS_FEEDS)
    logging.info(f"Fetched {len(feed_results)} feed results.")

    # Extract data from feed results
    feed_data_list = []
    for feed_entry in feed_results[:1]:  # Process first feed for now
            url, data = feed_entry
            if data:  # Make sure data is not None
                logging.info(f"Processing feed from {url}")
                entries = data.entries[:5]
                logging.info(f"Extracted {len(entries)} entries from {url}")
                feed_data_list.append(entries)
            else:
                logging.warning(f"No data for feed entry from {url}")

    if feed_data_list:
        logging.info("Processing feeds in batch with AI.")
        # Process all feeds in batch
        batch_results = await process_rss_with_ai_in_batch(
            feed_data_list,
            model="gpt-4.1",
        )
        logging.info("Finished processing feeds in batch with AI.")
        return batch_results
    else:
        logging.warning("No valid feed data to process.")
        return []



async def post_feeds(
    feed_results,
):
    """
    Main function to process multiple feeds asynchronously and send to Telegram.

    Args:
        telegram_channel_id: Telegram channel ID to send messages to
    """
    logging.info(f"Posting {len(feed_results)} feed results to Telegram.")
    telegram_channel_id_str = os.environ.get("TELEGRAM_CHANNEL_ID")
    if not telegram_channel_id_str:
        logging.error("TELEGRAM_CHANNEL_ID environment variable not set.")
        return feed_results

    try:
        telegram_channel_id = int(telegram_channel_id_str)
    except ValueError:
        logging.error("TELEGRAM_CHANNEL_ID is not a valid integer.")
        return feed_results

    for result in feed_results:
        try:
            response = result["response"]
            body = response["body"]
            choices = body["choices"][0]
            content = choices["message"]["content"]
            if content is not None:
                logging.info("Sending message to Telegram channel.")
                await send_message_to_channel(message=content, telegram_channel_id=telegram_channel_id)
                logging.info("Message sent successfully.")
            else:
                logging.warning("Content is None, not sending message.")
        except (KeyError, IndexError) as e:
            logging.error(f"Error processing result: {e} - result was: {result}")


    logging.info("Finished posting feed results to Telegram.")
    return feed_results
