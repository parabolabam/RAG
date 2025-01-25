import os
from dotenv import load_dotenv
from fastapi import APIRouter
from .github_trending.github_trends_searcher import (
    fetch_github_trending,
)
from senpy_ai_chatbot.features.send_channel_message import send_message_to_channel

from .github_trending.process_github_trends_with_ai import (
    process_github_trends,
)

load_dotenv()

router = APIRouter()


@router.get("/github-trends")
async def fetch_github_trends(language: str | None = None, limit: int = 5):
    return await fetch_github_trending(language, limit)


@router.post("/github-trends")
async def post_github_trends_to_channel(language: str | None = None, limit: int = 10):
    processed_trends = await process_github_trends(language, limit)
    channel_id = int(os.getenv("TELEGRAM_CHANNEL_ID") or "-1")
    await send_message_to_channel(channel_id, processed_trends)
    return processed_trends
