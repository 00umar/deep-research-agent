from loguru import logger


def earnings_summary(company_name: str = "", **_kwargs) -> dict:
    """Research a company's most recent earnings results and analyst reactions."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Earnings summary for: {company_name}")
        task = (
            f"Research the most recent earnings results for {company_name}.\n"
            f"1. Search for '{company_name} earnings results Q1 Q2 Q3 Q4 2024 2025'\n"
            f"2. Find: actual EPS vs estimates, revenue vs estimates, guidance\n"
            f"3. Note whether the company beat or missed analyst expectations\n"
            f"4. Find analyst reactions and any stock price movement after earnings\n"
            "Summarize: BEAT, MISSED, or IN-LINE with estimates, and key takeaways."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()

        outcome = "UNKNOWN"
        content = result.get("result", "").upper()
        if "BEAT" in content:
            outcome = "BEAT"
        elif "MISSED" in content or "MISS" in content:
            outcome = "MISSED"
        elif "IN-LINE" in content or "IN LINE" in content:
            outcome = "IN-LINE"

        return {
            "company": company_name,
            "earnings_outcome": outcome,
            "summary": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


earnings_summary_declaration = {
    "type": "function",
    "function": {
        "name": "earnings_summary",
        "description": (
            "Research a company's most recent quarterly earnings: EPS, revenue, guidance, and analyst reactions. "
            "Returns BEAT / MISSED / IN-LINE verdict vs estimates. "
            "Use in the analyze phase to assess recent financial performance."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to look up earnings for (e.g. 'Apple Inc')"}
            },
            "required": ["company_name"]
        }
    }
}
