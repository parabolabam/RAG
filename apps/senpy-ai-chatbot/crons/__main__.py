from senpy_ai_chatbot.features.news.github_trending.post_github_trends import (
    post_github_trends,
)
import asyncio


async def main():
    await post_github_trends(None, 5)


if __name__ == "__main__":
    print("Running cron...")
    asyncio.run(main())
