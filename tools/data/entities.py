import os
import time
import json
from openai import OpenAI, RateLimitError


def extract_entities(text: str) -> dict:
    """Extract named entities (people, organizations, places, products, dates) from text."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        prompt = f"""Extract named entities from this text. Return ONLY a JSON object with these exact keys:
{{"people": [], "organizations": [], "places": [], "products": [], "dates": []}}

No explanation, just the JSON.

Text:
{text[:3000]}"""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content.strip()
                start, end = raw.find("{"), raw.rfind("}") + 1
                entities = json.loads(raw[start:end]) if start >= 0 else {}
                return {"entities": entities}
            except RateLimitError:
                time.sleep(65)
        return {"entities": {}, "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


extract_entities_declaration = {
    "type": "function",
    "function": {
        "name": "extract_entities",
        "description": "Extract named entities from text: people, organizations, places, products, and dates. Use to identify the key players and context in research material.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to extract entities from"}
            },
            "required": ["text"]
        }
    }
}
