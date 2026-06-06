from loguru import logger


def fact_check(claim: str) -> dict:
    """Verify a specific claim by searching for confirming or contradicting evidence."""
    try:
        from agent.subagent import SubAgent

        logger.info(f"Fact checking: {claim[:60]}")

        task = (
            f'Verify this specific claim: "{claim}"\n\n'
            "Steps:\n"
            "1. Search for evidence that directly confirms or contradicts this claim\n"
            "2. Search for the original source if possible\n"
            "3. Search for counter-evidence or corrections\n\n"
            "End your response with exactly one of these verdicts:\n"
            "VERDICT: CONFIRMED\n"
            "VERDICT: DISPUTED\n"
            "VERDICT: FALSE\n"
            "VERDICT: UNVERIFIED\n\n"
            "Then explain your reasoning with the specific evidence you found."
        )

        agent = SubAgent(task=task, allowed_tools=["web_search", "web_scrape", "text_summarize"])
        result = agent.run()

        verdict = "UNVERIFIED"
        for v in ["CONFIRMED", "DISPUTED", "FALSE", "UNVERIFIED"]:
            if f"VERDICT: {v}" in result["result"].upper():
                verdict = v
                break

        return {
            "claim": claim,
            "verdict": verdict,
            "evidence": result["result"],
            "tool_calls_made": result["tool_calls_made"],
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "claim": claim}


fact_check_declaration = {
    "type": "function",
    "function": {
        "name": "fact_check",
        "description": (
            "Verify a specific claim by searching for confirming or contradicting evidence. "
            "Returns a verdict: CONFIRMED, DISPUTED, FALSE, or UNVERIFIED. "
            "Use before including a major claim in the final report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {"type": "string", "description": "The specific claim to verify"}
            },
            "required": ["claim"]
        }
    }
}
