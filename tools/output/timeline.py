import os
import time
from openai import OpenAI, RateLimitError


def build_timeline(text: str, topic: str = "") -> dict:
    """Extract events and dates from text and format as a chronological timeline."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        topic_line = f" about: {topic}" if topic else ""
        prompt = f"""From the text below, extract all events with specific dates or years to build a chronological timeline{topic_line}.

Format each item as:
- **[DATE/YEAR]** — Event description

Order from oldest to newest. Only include events with a date or year explicitly mentioned.

Text:
{text[:4000]}"""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return {"timeline": response.choices[0].message.content.strip(), "topic": topic}
            except RateLimitError:
                time.sleep(65)
        return {"timeline": "", "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


build_timeline_declaration = {
    "type": "function",
    "function": {
        "name": "build_timeline",
        "description": "Extract events and dates from text and format them as a chronological timeline. Use for historical topics or to show how something developed over time.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text containing events and dates"},
                "topic": {"type": "string", "description": "Optional topic label for the timeline"}
            },
            "required": ["text"]
        }
    }
}
