import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def link_extractor(url: str, same_domain_only: bool = False) -> dict:
    """Extract all hyperlinks from a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        response = httpx.get(url, timeout=15, follow_redirects=True, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        base_domain = urlparse(url).netloc
        seen = set()
        links = []
        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            if not full_url.startswith("http"):
                continue
            if same_domain_only and urlparse(full_url).netloc != base_domain:
                continue
            if full_url in seen:
                continue
            seen.add(full_url)
            links.append({"url": full_url, "text": a.get_text(strip=True)[:100]})
        return {"source_url": url, "links": links[:50], "count": len(links)}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "url": url}


link_extractor_declaration = {
    "type": "function",
    "function": {
        "name": "link_extractor",
        "description": "Extract all hyperlinks from a webpage. Use after scraping a page to discover related sources, references, or deeper content worth investigating.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to extract links from"},
                "same_domain_only": {"type": "boolean", "description": "Only return links from the same domain (default false)"}
            },
            "required": ["url"]
        }
    }
}
