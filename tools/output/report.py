import os
from datetime import datetime
from models.schemas import ResearchReport
from google.genai import types


def compile_report(title: str, query: str, findings: str, sources: list = None) -> dict:
    """Compile research findings into a structured markdown report and save it."""
    try:
        report = ResearchReport(
            title=title,
            query=query,
            summary=findings,
            sections=[{"content": findings}],
            sources=sources or [],
            word_count=len(findings.split())
        )

        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/report_{timestamp}.md"

        sources_md = "\n".join(f"- {s}" for s in (sources or [])) or "_No sources recorded._"
        md = f"""# {title}

**Query:** {query}
**Generated:** {report.created_at}

## Summary

{findings}

## Sources

{sources_md}
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)

        return {**report.model_dump(), "saved_to": filename}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


compile_report_declaration = types.FunctionDeclaration(
    name="compile_report",
    description="Compile all research findings into a structured markdown report and save it. Use this as the final step after gathering all information.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "title": types.Schema(type=types.Type.STRING, description="Report title"),
            "query": types.Schema(type=types.Type.STRING, description="Original research query"),
            "findings": types.Schema(type=types.Type.STRING, description="All compiled research findings"),
            "sources": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="List of source URLs used"
            )
        },
        required=["title", "query", "findings"]
    )
)
