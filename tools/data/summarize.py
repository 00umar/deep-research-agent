import os
from google import genai
from google.genai import types
from models.schemas import SummaryResult


def text_summarize(text: str, max_points: int = 5) -> dict:
    """Summarize text and extract key points using Gemini."""
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = f"""Summarize the following text and extract {max_points} key points.

Format your response exactly like this:
SUMMARY: [one paragraph summary]
KEY_POINTS:
- [point 1]
- [point 2]

Text:
{text[:4000]}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw = response.text

        summary = raw
        key_points = []

        if "SUMMARY:" in raw and "KEY_POINTS:" in raw:
            parts = raw.split("KEY_POINTS:")
            summary = parts[0].replace("SUMMARY:", "").strip()
            key_points = [
                line.strip().lstrip("- ").strip()
                for line in parts[1].splitlines()
                if line.strip().startswith("-")
            ]

        return SummaryResult(
            original_length=len(text.split()),
            summary=summary,
            key_points=key_points
        ).model_dump()
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


text_summarize_declaration = types.FunctionDeclaration(
    name="text_summarize",
    description="Summarize a long text and extract key points. Use after scraping a page to distill the most important information before storing it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "text": types.Schema(type=types.Type.STRING, description="The text to summarize"),
            "max_points": types.Schema(type=types.Type.INTEGER, description="Max key points to extract (default 5)")
        },
        required=["text"]
    )
)
