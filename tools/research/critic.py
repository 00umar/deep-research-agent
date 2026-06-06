import os
import time
from openai import OpenAI, RateLimitError


def critic_review(draft: str, original_query: str) -> dict:
    """Have a critical AI editor review a draft report and identify gaps."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        prompt = f"""You are a critical research editor. Review this draft report and identify what is missing or weak.

ORIGINAL RESEARCH QUERY: {original_query}

DRAFT REPORT:
{draft[:5000]}

Provide your review in these sections:

GAPS: Important topics the query asked about that the report missed or under-covered.
WEAKNESSES: Claims made without sufficient evidence.
IMPROVEMENTS: Specific suggestions to make the report stronger.
MISSING_SOURCES: Types of sources that should be consulted but were not mentioned.

Be specific and actionable. If the report is thorough, say so."""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return {
                    "review": response.choices[0].message.content.strip(),
                    "query": original_query,
                    "draft_word_count": len(draft.split()),
                }
            except RateLimitError:
                time.sleep(65)
        return {"review": "", "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


critic_review_declaration = {
    "type": "function",
    "function": {
        "name": "critic_review",
        "description": (
            "Have a critical AI editor review a draft report and identify gaps, "
            "unsupported claims, and missing sources. Use after compiling a first draft "
            "to find what is missing before finalizing the report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "draft": {"type": "string", "description": "The draft report text to review"},
                "original_query": {"type": "string", "description": "The original research question"}
            },
            "required": ["draft", "original_query"]
        }
    }
}
