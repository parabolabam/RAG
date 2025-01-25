# Function to scrape and summarize news from a given source

import requests
from bs4 import BeautifulSoup
from textwrap import shorten


def fetch_news(url, limit=5):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Find headlines (customize this selector based on the site)
        headlines = [h.get_text() for h in soup.find_all("h3")][:limit]

        summaries = []
        for idx, headline in enumerate(headlines):
            summary = shorten(headline, width=100, placeholder="...")
            summaries.append(f"{idx + 1}. {summary}")

        return "\n".join(summaries)
    except Exception as e:
        return f"Failed to fetch news: {e}"
