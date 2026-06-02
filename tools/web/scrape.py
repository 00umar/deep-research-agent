import httpx
from bs4 import BeautifulSoup
from models.schemas import ScrapeResult
from google.genai import types


def web_scrape(url: str) -> dict:
    """Scrape and extract clean text content from a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
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


web_scrape_declaration = types.FunctionDeclaration(
    name="web_scrape",
    description="Scrape the full text content from a webpage URL. Use after web_search to get detailed information from a specific source.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "url": types.Schema(type=types.Type.STRING, description="The full URL to scrape")
        },
        required=["url"]
    )
)
