from loguru import logger


def company_profile(company_name: str) -> dict:
    """Get a comprehensive company overview: founding, business model, key products, size."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Company profile for: {company_name}")
        task = (
            f"Research a comprehensive profile of {company_name}.\n"
            "1. Find founding year, headquarters, CEO, and number of employees\n"
            "2. Describe the core business model and main revenue streams\n"
            "3. List the top 3 products or services\n"
            "4. Find annual revenue and market cap if available\n"
            "5. Note any recent major news (last 12 months)\n"
            "Structure your response with clear sections for each point above."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "web_scrape", "text_summarize"])
        result = agent.run()
        return {
            "company": company_name,
            "profile": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


company_profile_declaration = {
    "type": "function",
    "function": {
        "name": "company_profile",
        "description": (
            "Get a comprehensive overview of a company: founding, CEO, employees, business model, "
            "main products, revenue, and recent news. "
            "Use at the start of due diligence to establish a baseline understanding of the target company."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to profile (e.g. 'Apple Inc', 'Stripe')"}
            },
            "required": ["company_name"]
        }
    }
}


def leadership_research(company_name: str) -> dict:
    """Research key executives, their backgrounds, tenure, and any controversies."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Leadership research for: {company_name}")
        task = (
            f"Research the key executives at {company_name} and their backgrounds.\n"
            f"1. Find the CEO, CFO, and other C-suite members\n"
            f"2. Research each leader's tenure and prior experience\n"
            f"3. Search for any executive controversies, departures, or insider trading alerts\n"
            f"4. Note any recent leadership changes in the last 2 years\n"
            "Flag any governance concerns. End with LEADERSHIP_RISK: LOW, MEDIUM, or HIGH."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()

        risk = "UNKNOWN"
        content = result.get("result", "").upper()
        for level in ["HIGH", "MEDIUM", "LOW"]:
            if f"LEADERSHIP_RISK: {level}" in content:
                risk = level
                break

        return {
            "company": company_name,
            "leadership_risk": risk,
            "findings": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


leadership_research_declaration = {
    "type": "function",
    "function": {
        "name": "leadership_research",
        "description": (
            "Research a company's key executives: CEO, CFO, board members. "
            "Checks for leadership tenure, prior experience, controversies, and recent departures. "
            "Returns a LEADERSHIP_RISK level. Use in the gather phase of due diligence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to research leadership for"}
            },
            "required": ["company_name"]
        }
    }
}


def market_position(company_name: str, sector: str = "") -> dict:
    """Assess a company's market share, brand strength, and industry ranking."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Market position for: {company_name}")
        sector_hint = f" in the {sector} sector" if sector else ""
        task = (
            f"Assess {company_name}'s market position{sector_hint}.\n"
            "1. Find estimated market share percentage if available\n"
            "2. Find industry ranking (e.g. #1, #2, #3 player)\n"
            "3. Assess brand strength and customer loyalty indicators\n"
            "4. Find recent wins or losses of major contracts/customers\n"
            "Rate the market position: DOMINANT, STRONG, MODERATE, or WEAK with evidence."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "web_scrape", "text_summarize"])
        result = agent.run()

        position = "UNKNOWN"
        content = result.get("result", "").upper()
        for label in ["DOMINANT", "STRONG", "MODERATE", "WEAK"]:
            if label in content:
                position = label
                break

        return {
            "company": company_name,
            "market_position": position,
            "analysis": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


market_position_declaration = {
    "type": "function",
    "function": {
        "name": "market_position",
        "description": (
            "Assess a company's market share, industry ranking, and brand strength. "
            "Returns a position label: DOMINANT / STRONG / MODERATE / WEAK. "
            "Use in the analyze phase to understand competitive standing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to assess"},
                "sector": {"type": "string", "description": "Industry sector for context (optional)"}
            },
            "required": ["company_name"]
        }
    }
}
