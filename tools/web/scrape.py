import httpx
from bs4 import BeautifulSoup
from models.schemas import ScrapeResult


_BLOCKED_DOMAINS = ("sec.gov/Archives", "sec.gov/cgi-bin")

def web_scrape(url: str) -> dict:
    """Scrape and extract clean text content from a webpage."""
    try:
        if any(d in url for d in _BLOCKED_DOMAINS):
            return {
                "error": "BlockedDomain",
                "message": (
                    "SEC.gov direct document URLs return 403. "
                    "Use sec_search or fetch_10k_summary instead to get filing data."
                ),
                "url": url,
            }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = httpx.get(url, timeout=15, follow_redirects=True, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        content = soup.get_text(separator="\n", strip=True)
        content = "\n".join(line for line in content.splitlines() if line.strip())

        return ScrapeResult(
            url=url,
            title=title,
            content=content[:8000],
            word_count=len(content.split())
        ).model_dump()
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "url": url}


web_scrape_declaration = {
    "type": "function",
    "function": {
        "name": "web_scrape",
        "description": "Scrape the full text content from a webpage URL. Use after web_search to get detailed information from a specific source.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The full URL to scrape"}
            },
            "required": ["url"]
        }
    }
}
