import aiohttp


async def fetch_text(url: str):
    """
    Fetch raw text from a URL using aiohttp.
    Raises if the request fails or non-OK status.
    """

    if not url:
        raise ValueError("URL is required")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
