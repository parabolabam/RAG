import json
from typing import List

from dataclasses import dataclass

from senpy_ai_news_report.features.ai.openai_client import AiNewsClient
from .github_trends_searcher import GithubTrending, fetch_github_trending
from .github_trends_prompts import github_trends_system_promt, github_trends_user_promt


@dataclass
class Trend:
    repository: str
    description: str
    stars: str
    language: str


@dataclass
class TrendsData:
    trends: List[Trend]


async def process_trends_with_ai(trends: list[GithubTrending]):
    """
    Process GitHub trends with AI.
    """

    return await AiNewsClient().process_news(
        github_trends_system_promt, github_trends_user_promt, json.dumps(trends)
    )


async def process_github_trends(language: str | None = None, limit: int = 10):
    """
    Fetch GitHub trending repositories and process them with AI.
    """
    # Fetch the trending repositories
    trends = await fetch_github_trending(language, limit)

    # Process the trends with AI
    processed_trends = await process_trends_with_ai(trends)

    processed_trends_json = processed_trends.choices[0].message.content or ""

    return processed_trends_json
