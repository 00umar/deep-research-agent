from loguru import logger


def multi_perspective_research(topic: str) -> dict:
    """Research a topic from 3 angles: supportive, critical, and factual."""
    try:
        from agent.subagent import SubAgent

        logger.info(f"Multi-perspective research: {topic[:50]}")

        perspectives = {
            "supportive": (
                f"Research the BENEFITS, ADVANTAGES, and SUCCESS CASES of: {topic}. "
                "Focus on positive evidence, why people support it, and what it does well."
            ),
            "critical": (
                f"Research the DRAWBACKS, CRITICISMS, FAILURES, and RISKS of: {topic}. "
                "Focus on problems, limitations, what critics say, and known failures."
            ),
            "factual": (
                f"Research OBJECTIVE FACTS, DATA, STATISTICS, and NUMBERS about: {topic}. "
                "Focus only on verifiable data, dates, figures, and neutral descriptions."
            ),
        }

        results = {}
        for angle, task in perspectives.items():
            logger.info(f"  Subagent [{angle}] starting...")
            agent = SubAgent(task=task, allowed_tools=["web_search", "web_scrape", "text_summarize"])
            results[angle] = agent.run()

        return {
            "topic": topic,
            "supportive_view": results["supportive"]["result"],
            "critical_view": results["critical"]["result"],
            "factual_data": results["factual"]["result"],
            "total_tool_calls": sum(r["tool_calls_made"] for r in results.values()),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "topic": topic}


multi_perspective_research_declaration = {
    "type": "function",
    "function": {
        "name": "multi_perspective_research",
        "description": (
            "Research a topic from 3 angles simultaneously: supportive (benefits/advantages), "
            "critical (drawbacks/risks), and factual (data/statistics). Produces a balanced, "
            "nuanced view. Use for controversial topics or any subject that needs thorough analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic to research from multiple perspectives"}
            },
            "required": ["topic"]
        }
    }
}
