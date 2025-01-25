from dotenv import load_dotenv
from senpy_ai_chatbot.features.news.github_trending.process_github_trends_with_ai import (
    process_github_trends,
)
from senpy_ai_chatbot.features.telegram_integration_features.send_channel_message import (
    send_message_to_channel,
)


load_dotenv()


async def post_github_trends(language: str | None, limit: int):
    processed_trends = await process_github_trends(language, limit)
    await send_message_to_channel(processed_trends)
    return processed_trends
