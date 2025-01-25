import os
from dotenv import load_dotenv
from senpy_ai_chatbot.features.news.github_trending.process_github_trends_with_ai import (
    process_github_trends,
)
from senpy_ai_chatbot.features.send_channel_message import send_message_to_channel


load_dotenv()


async def post_github_trends(language: str | None, limit: int):
    processed_trends = await process_github_trends(language, limit)
    channel_id = int(os.getenv("TELEGRAM_CHANNEL_ID") or "-1")
    await send_message_to_channel(channel_id, processed_trends)
    return processed_trends
