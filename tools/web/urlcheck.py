import httpx


def url_check(url: str) -> dict:
    """Check if a URL is alive and accessible."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        response = httpx.head(url, timeout=10, follow_redirects=True, headers=headers)
        return {
            "url": url,
            "alive": response.status_code < 400,
            "status_code": response.status_code,
            "final_url": str(response.url)
        }
    except httpx.TimeoutException:
        return {"url": url, "alive": False, "status_code": None, "error": "Timeout"}
    except Exception as e:
        return {"url": url, "alive": False, "status_code": None, "error": str(e)}


url_check_declaration = {
    "type": "function",
    "function": {
        "name": "url_check",
        "description": "Check if a URL is alive and accessible before scraping it. Use to avoid wasting time on dead or broken links.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to check"}
            },
            "required": ["url"]
        }
    }
}
