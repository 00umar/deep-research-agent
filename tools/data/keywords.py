import os
import time
import json
from openai import OpenAI, RateLimitError


def extract_keywords(text: str, max_keywords: int = 10) -> dict:
    """Extract the most important keywords and phrases from text."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        prompt = f"""Extract the {max_keywords} most important keywords and key phrases from this text.
Return ONLY a JSON array of strings, no explanation. Example: ["keyword1", "key phrase 2", "term3"]

Text:
{text[:3000]}"""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content.strip()
                start, end = raw.find("["), raw.rfind("]") + 1
                keywords = json.loads(raw[start:end]) if start >= 0 else []
                return {"keywords": keywords, "count": len(keywords)}
            except RateLimitError:
                time.sleep(65)
        return {"keywords": [], "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


extract_keywords_declaration = {
    "type": "function",
    "function": {
        "name": "extract_keywords",
        "description": "Extract the most important keywords and key phrases from a text. Use to identify what to search for next or to understand what a document is about.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to extract keywords from"},
                "max_keywords": {"type": "integer", "description": "Maximum number of keywords to extract (default 10)"}
            },
            "required": ["text"]
        }
    }
}
