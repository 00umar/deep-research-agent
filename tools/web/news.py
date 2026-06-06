from ddgs import DDGS


def news_search(query: str, max_results: int = 5) -> dict:
    """Search for recent news articles using DuckDuckGo news."""
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.news(query, max_results=max_results))
        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("body", ""),
                "source": r.get("source", ""),
                "date": r.get("date", "")
            }
            for r in raw
        ]
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "query": query}


news_search_declaration = {
    "type": "function",
    "function": {
        "name": "news_search",
        "description": "Search for recent news articles on a topic. Use this instead of web_search when you need current events, breaking news, or the latest developments on a subject.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The news search query"},
                "max_results": {"type": "integer", "description": "Number of results to return (default 5)"}
            },
            "required": ["query"]
        }
    }
}
