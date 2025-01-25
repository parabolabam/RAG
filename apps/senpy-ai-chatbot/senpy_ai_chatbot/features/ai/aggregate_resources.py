# Function to aggregate news from all sources
from clients.ai import NewsOpenAi
from typing import List


# Function to summarize news using OpenAI Python Batch API
def summarize_news(raw_texts: List[str]) -> List[str]:
    client = NewsOpenAi()
    try:
        # Prepare prompts for each text
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that summarizes developer-related news articles.",
            },
            [
                {
                    "role": "user",
                    "content": text[:2000],
                }
                for text in raw_texts
            ],
        ]

        summaries = []
        for message in messages:
            response = client.client.chat.completions.create(
                model="gpt-4", messages=message
            )
            summaries.append(response.choices[0].message.content)

        return summaries

    except Exception as e:
        return [f"Failed to summarize: {str(e)}"]
