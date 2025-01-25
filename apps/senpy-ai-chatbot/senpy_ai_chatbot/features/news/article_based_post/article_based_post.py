from senpy_ai_chatbot.features.ai.openai_client import AiNewsClient
from .article_prompts import (
    article_system_promt,
    article_user_promt,
)


async def process_article_with_ai(link: str):
    """
    Process Article with AI.
    """

    return await AiNewsClient().process_news(
        system_prompt=article_system_promt,
        user_prompt=article_user_promt,
        data=f"here is the article link: {link}",
    )


async def process_article(link: str):
    """
    Fetch GitHub trending repositories and process them with AI.
    """
    # Fetch the trending repositories

    # Process the trends with AI
    processed_trends = await process_article_with_ai(link)

    processed_article_blogpost = processed_trends.choices[0].message.content or ""

    return processed_article_blogpost
