import os
import time
from openai import OpenAI, RateLimitError
from models.schemas import SummaryResult


def _generate_with_retry(client, prompt: str, max_retries: int = 6) -> str:
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except RateLimitError:
            time.sleep(65)
    raise RuntimeError("Max retries exceeded on rate limit.")


def text_summarize(text: str, max_points: int = 5) -> dict:
    """Summarize text and extract key points using Groq/Llama."""
    try:
        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        prompt = f"""Summarize the following text and extract {max_points} key points.

Format your response exactly like this:
SUMMARY: [one paragraph summary]
KEY_POINTS:
- [point 1]
- [point 2]

Text:
{text[:4000]}"""

        raw = _generate_with_retry(client, prompt)
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


text_summarize_declaration = {
    "type": "function",
    "function": {
        "name": "text_summarize",
        "description": "Summarize a long text and extract key points. Use after scraping a page to distill the most important information before storing it.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to summarize"},
                "max_points": {"type": "integer", "description": "Max key points to extract (default 5)"}
            },
            "required": ["text"]
        }
    }
}
