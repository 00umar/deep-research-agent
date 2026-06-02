from ddgs import DDGS
from models.schemas import SearchResult
from google.genai import types


def web_search(query: str, max_results: int = 5) -> dict:
    """Search the web using DuckDuckGo. Returns titles, URLs, and snippets."""
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))
        results = [
            {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
            for r in raw
        ]
        return SearchResult(query=query, results=results).model_dump()
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "query": query}


web_search_declaration = types.FunctionDeclaration(
    name="web_search",
    description="Search the web for information on a topic. Returns a list of relevant results with titles, URLs, and snippets. Use this first to discover sources.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(type=types.Type.STRING, description="The search query"),
            "max_results": types.Schema(type=types.Type.INTEGER, description="Number of results (default 5)")
        },
        required=["query"]
    )
)
