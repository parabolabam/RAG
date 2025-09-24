import json
import os
from typing import List

_DEFAULT_FEEDS = [
    # "https://github.com/oven-sh/bun/releases.atom",
    # "https://github.com/angular/angular/tags.atom",
    # "https://dev.to/rss",
    "https://openai.com/news/rss.xml",
]


def _parse_feeds(raw: str) -> List[str]:
    raw = raw.strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, list):
        return [str(item).strip() for item in data if str(item).strip()]

    values = raw.replace(";", ",").replace("\n", ",").replace("\r", ",")
    return [entry.strip() for entry in values.split(",") if entry.strip()]


_ENV_FEEDS = _parse_feeds(os.getenv("FEEDS", ""))
RSS_FEEDS = _ENV_FEEDS or _DEFAULT_FEEDS
