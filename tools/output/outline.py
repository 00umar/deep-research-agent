import os
import time
from openai import OpenAI, RateLimitError


def generate_outline(topic: str, findings: str = "") -> dict:
    """Generate a structured report outline for a research topic."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        context = f"\n\nFindings gathered so far:\n{findings[:2000]}" if findings else ""
        prompt = f"""Create a comprehensive report outline for a research report on: {topic}{context}

Format as a numbered outline:
1. Introduction
   1.1 ...
2. ...

Include 5-8 main sections with sub-points. Make it logical and thorough."""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return {"outline": response.choices[0].message.content.strip(), "topic": topic}
            except RateLimitError:
                time.sleep(65)
        return {"outline": "", "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


generate_outline_declaration = {
    "type": "function",
    "function": {
        "name": "generate_outline",
        "description": "Generate a structured outline for a research report. Use at the start of research to plan what sections to cover before diving in.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The research topic to outline"},
                "findings": {"type": "string", "description": "Optional summary of findings gathered so far to inform the outline"}
            },
            "required": ["topic"]
        }
    }
}
