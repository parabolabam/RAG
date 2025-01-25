from dotenv import load_dotenv
from fastapi import APIRouter

from senpy_ai_chatbot.features.news.github_trending.post_github_trends import (
    post_github_trends,
)
from .github_trending.github_trends_searcher import (
    fetch_github_trending,
)


load_dotenv()

router = APIRouter()


@router.get("/github-trends")
async def fetch_github_trends(language: str | None = None, limit: int = 10):
    return await fetch_github_trending(language, limit)


@router.post("/github-trends")
async def post_github_trends_to_channel(language: str | None = None, limit: int = 10):
    return await post_github_trends(language, limit)
