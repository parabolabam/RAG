from senpy_ai_news_report.features.news.article_based_post.article_based_post import (
    process_article,
)
from senpy_ai_news_report.features.telegram_integration_features.send_channel_message import (
    send_message_to_channel,
)


async def create_and_post_blogpost(
    link: str,
):
    processed_article = await process_article(link)
    return await send_message_to_channel(processed_article)
