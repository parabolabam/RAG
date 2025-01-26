from dotenv import load_dotenv
from fastapi import APIRouter

from senpy_ai_chatbot.features.news.article_based_post.models.article import Article
from senpy_ai_chatbot.features.news.article_based_post.post_article import (
    create_and_post_blogpost,
)
from senpy_ai_chatbot.features.news.github_trending.post_github_trends import (
    post_github_trends,
)
from senpy_ai_chatbot.features.news.rss.feed_parser import parse_feeds
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


@router.post("/post-article")
async def post_article_to_channel(article: Article):
    return await create_and_post_blogpost(article.link)


@router.post("/parse-feeds")
async def post_feeds():
    return await parse_feeds()
