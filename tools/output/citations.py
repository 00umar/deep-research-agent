def format_citations(sources: list, style: str = "numbered") -> dict:
    """Format a list of URLs or source dicts into proper citations."""
    try:
        citations = []
        for i, source in enumerate(sources, 1):
            if isinstance(source, str):
                url, title = source, ""
            elif isinstance(source, dict):
                url = source.get("url", "")
                title = source.get("title", "")
            else:
                continue

            if style == "numbered":
                prefix = f"[{i}]"
                body = f"{title} — {url}" if title else url
            else:
                prefix = "-"
                body = f"{title}: {url}" if title else url

            citations.append({"index": i, "url": url, "title": title, "formatted": f"{prefix} {body}"})

        formatted_text = "\n".join(c["formatted"] for c in citations)
        return {"citations": citations, "formatted_text": formatted_text, "count": len(citations)}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


format_citations_declaration = {
    "type": "function",
    "function": {
        "name": "format_citations",
        "description": "Format a list of source URLs into numbered citations for use in a report.",
        "parameters": {
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of source URLs to format as citations"
                },
                "style": {"type": "string", "description": "Citation style: 'numbered' (default) or 'bullet'"}
            },
            "required": ["sources"]
        }
    }
}
