from bs4 import BeautifulSoup
from senpy_ai_news_report.utils import fetch_text
from senpy_ai_news_report.utils.serializable_dataclass import SerilizableDataclass


class GithubTrending(SerilizableDataclass):
    def __init__(self, repo_name: str, repo_description: str, full_repo_url: str):
        self.repo_name = repo_name
        self.repo_description = repo_description
        self.full_repo_url = full_repo_url


async def fetch_github_trending(language=None, limit=5) -> list[GithubTrending]:
    """
    Scrape GitHub Trending. If 'language' is None, fetch the overall trending page.
    If 'language' is provided, fetch that language's trending page.

    Returns a list of (repo_name, repo_description, repo_url).
    """

    if language:
        url = f"https://github.com/trending/{language}?since=daily"
    else:
        url = "https://github.com/trending?since=daily"

    try:
        html = await fetch_text.fetch_text(url)
        soup = BeautifulSoup(html, "html.parser")
        # Each repo item is typically an <article> with class "Box-row"
        repo_rows = soup.find_all("article", class_="Box-row")
        repos = []
        for row in repo_rows[:limit]:
            h2 = row.find("h2")
            if not h2:
                continue
            link_tag = h2.find("a")
            if not link_tag:
                continue

            # e.g. "/owner/repo"
            repo_link = link_tag.get("href", "").strip()
            repo_name = repo_link.strip("/")

            full_repo_url = f"https://github.com{repo_link}"

            desc_tag = row.find("p")
            repo_desc = desc_tag.get_text(strip=True) if desc_tag else "No description"

            repos.append(
                {
                    "repo_name": repo_name,
                    "repo_desc": repo_desc,
                    "full_repo_url": full_repo_url,
                }
            )

        return repos

    except Exception as e:
        print(f"[ERROR] Could not scrape GitHub trending - {e}")
        return []
