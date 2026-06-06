import os
import time
from openai import OpenAI, RateLimitError


def comparison_matrix(items: list, criteria: list = None) -> dict:
    """Create a structured side-by-side comparison table for multiple items."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        items_text = "\n".join(f"- {item}" for item in items)
        criteria_text = ", ".join(criteria) if criteria else "key features, pros, cons, use cases, pricing/availability"
        prompt = f"""Create a detailed comparison of these items:
{items_text}

Compare across these criteria: {criteria_text}

Format as a clean markdown table. Be concise and factual."""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return {"comparison": response.choices[0].message.content.strip(), "items": items}
            except RateLimitError:
                time.sleep(65)
        return {"comparison": "", "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


comparison_matrix_declaration = {
    "type": "function",
    "function": {
        "name": "comparison_matrix",
        "description": "Create a structured comparison table of multiple items across key criteria. Perfect for comparing products, frameworks, tools, or competing options side-by-side.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of items to compare"
                },
                "criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Criteria to compare on (optional — defaults to features, pros, cons, use cases)"
                }
            },
            "required": ["items"]
        }
    }
}
