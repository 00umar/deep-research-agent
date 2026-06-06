import os
import time
from openai import OpenAI, RateLimitError


def detect_contradictions(text_a: str, text_b: str) -> dict:
    """Find contradictions or conflicting claims between two research texts."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        prompt = f"""Compare these two texts and identify contradictions or conflicting claims.

TEXT A:
{text_a[:2000]}

TEXT B:
{text_b[:2000]}

For each contradiction found, write:
CONTRADICTION [N]:
- Text A claims: [quote or paraphrase]
- Text B claims: [quote or paraphrase]
- Significance: [low / medium / high]

If no contradictions exist, write: "No significant contradictions found."
Be specific. Only flag genuine factual conflicts, not differences in emphasis."""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                analysis = response.choices[0].message.content.strip()
                has_contradictions = "no significant contradictions" not in analysis.lower()
                return {"has_contradictions": has_contradictions, "analysis": analysis}
            except RateLimitError:
                time.sleep(65)
        return {"has_contradictions": False, "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


detect_contradictions_declaration = {
    "type": "function",
    "function": {
        "name": "detect_contradictions",
        "description": (
            "Compare two research texts and identify contradictions or conflicting claims. "
            "Use when two sources appear to disagree to surface the conflict explicitly "
            "rather than silently picking one version."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text_a": {"type": "string", "description": "First text to compare"},
                "text_b": {"type": "string", "description": "Second text to compare"}
            },
            "required": ["text_a", "text_b"]
        }
    }
}
