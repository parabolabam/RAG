from dotenv import load_dotenv
from fastapi import APIRouter

from senpy_ai_news_report.features.news.article_based_post.models.article import Article
from senpy_ai_news_report.features.news.article_based_post.post_article import (
    create_and_post_blogpost,
)
from senpy_ai_news_report.features.news.github_trending.post_github_trends import (
    post_github_trends,
)
from senpy_ai_news_report.features.news.rss.feed_parser import parse_feeds, post_feeds
from .github_trending.github_trends_searcher import (
    fetch_github_trending,
)


load_dotenv()

router = APIRouter()


@router.get("/github-trends")
async def fetch_github_trends(language: str | None = None, limit: int = 10):
    return await fetch_github_trending(language, limit)


@router.post("/post-github-trends-to-telegram-channel")
async def post_github_trends_to_channel(
    language: str | None = None, limit: int = 10, telegram_channel_id: int | None = None
):
    return await post_github_trends(language, limit, telegram_channel_id)


@router.post("/post-article")
async def post_article_to_channel(article: Article):
    return await create_and_post_blogpost(article.link)


@router.get("/parse-feeds")
async def parse_feeds_news():
    return await parse_feeds()


@router.post("/post-feeds-news")
async def post_feeds_news():

    parsed_feed = await parse_feeds()
    return await post_feeds(parsed_feed)
