from senpy_ai_chatbot.features.news.github_trending.post_github_trends import (
    post_github_trends,
)


async def github_trends_cron():
    await post_github_trends(None, 5)


cron_result = github_trends_cron()
