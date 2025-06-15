from senpy_ai_news_report.features.news.github_trending.process_github_trends_with_ai import (
    process_github_trends,
)
from senpy_ai_news_report.features.telegram_integration_features.send_channel_message import (
    send_message_to_channel,
)


async def post_github_trends(
    language: str | None, limit: int, telegram_channel_id: int | None
):
    processed_trends = await process_github_trends(language, limit)
    await send_message_to_channel(processed_trends, telegram_channel_id)
    return processed_trends



