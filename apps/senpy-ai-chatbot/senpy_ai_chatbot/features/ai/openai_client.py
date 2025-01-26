import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class AiNewsClient:
    async_client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
    )

    async def process_news(self, system_prompt: str, user_prompt: str, data: str):
        return await self.async_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.5,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"{user_prompt}, data: {data}",
                },
            ],
        )
