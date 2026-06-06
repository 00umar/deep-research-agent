import httpx
from bs4 import BeautifulSoup


def page_metadata(url: str) -> dict:
    """Get title, description, and publish date of a URL without full scraping."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        response = httpx.get(url, timeout=10, follow_redirects=True, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title")
        title = title.get_text(strip=True) if title else ""

        description = ""
        for attr in [{"name": "description"}, {"property": "og:description"}, {"name": "twitter:description"}]:
            tag = soup.find("meta", attrs=attr)
            if tag and tag.get("content"):
                description = tag["content"]
                break

        published = ""
        for attr in [
            {"property": "article:published_time"},
            {"name": "date"},
            {"name": "pubdate"},
            {"itemprop": "datePublished"}
        ]:
            tag = soup.find("meta", attrs=attr)
            if tag and tag.get("content"):
                published = tag["content"]
                break

        return {
            "url": url,
            "title": title,
            "description": description[:300],
            "published": published,
            "status_code": response.status_code
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "url": url}


page_metadata_declaration = {
    "type": "function",
    "function": {
        "name": "page_metadata",
        "description": "Quickly get the title, description, and publish date of a URL without fully scraping it. Use to evaluate if a source is worth reading before committing to a full scrape.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to get metadata for"}
            },
            "required": ["url"]
        }
    }
}
