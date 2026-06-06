import os
import time
from openai import OpenAI, RateLimitError


def confidence_score(claim: str, supporting_text: str) -> dict:
    """Rate how strongly the available evidence supports a claim."""
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        prompt = f"""Evaluate how strongly the provided evidence supports this claim.

CLAIM: {claim}

EVIDENCE:
{supporting_text[:3000]}

Rate the confidence as exactly one of:
- STRONG: Multiple independent sources confirm this with specific data or numbers
- MODERATE: Some evidence supports this but it is not definitive
- WEAK: Limited or indirect evidence, mostly single-source or speculative
- UNVERIFIED: No direct evidence found in the provided text

Respond in exactly this format:
CONFIDENCE: [STRONG/MODERATE/WEAK/UNVERIFIED]
REASONING: [1-2 sentence explanation]"""
        for attempt in range(4):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content.strip()
                level, reasoning = "UNVERIFIED", ""
                for line in raw.splitlines():
                    if line.startswith("CONFIDENCE:"):
                        for lvl in ["STRONG", "MODERATE", "WEAK", "UNVERIFIED"]:
                            if lvl in line.upper():
                                level = lvl
                                break
                    elif line.startswith("REASONING:"):
                        reasoning = line.replace("REASONING:", "").strip()
                return {"claim": claim, "confidence": level, "reasoning": reasoning}
            except RateLimitError:
                time.sleep(65)
        return {"claim": claim, "confidence": "UNVERIFIED", "error": "Max retries exceeded"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


confidence_score_declaration = {
    "type": "function",
    "function": {
        "name": "confidence_score",
        "description": (
            "Rate how strongly the available evidence supports a specific claim. "
            "Returns STRONG, MODERATE, WEAK, or UNVERIFIED with reasoning. "
            "Use before including a key claim in the final report to tag its reliability."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {"type": "string", "description": "The claim to evaluate"},
                "supporting_text": {"type": "string", "description": "The evidence text to evaluate against the claim"}
            },
            "required": ["claim", "supporting_text"]
        }
    }
}
