from loguru import logger


def acquisition_history(company_name: str) -> dict:
    """Find a company's past acquisitions, mergers, and divestitures."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Acquisition history for: {company_name}")
        task = (
            f"Research the acquisition and merger history of {company_name}.\n"
            f"1. Search for '{company_name} acquisitions history'\n"
            f"2. List major acquisitions with year and approximate deal value\n"
            f"3. Note any failed acquisition attempts or abandoned deals\n"
            f"4. Find any recent divestitures or spin-offs\n"
            "Summarize: total acquisitions made, biggest deals, and whether the M&A strategy has been successful."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()
        return {
            "company": company_name,
            "acquisition_history": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


acquisition_history_declaration = {
    "type": "function",
    "function": {
        "name": "acquisition_history",
        "description": (
            "Research a company's history of acquisitions, mergers, and divestitures. "
            "Returns a list of major deals with years and values. "
            "Use to understand growth strategy and integration risks."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to research M&A history for"}
            },
            "required": ["company_name"]
        }
    }
}


def supply_chain_analysis(company_name: str) -> dict:
    """Identify supply chain dependencies and concentration risks."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Supply chain analysis for: {company_name}")
        task = (
            f"Analyze the supply chain of {company_name}.\n"
            f"1. Search for major suppliers and manufacturing partners\n"
            f"2. Find any geographic concentration risks (e.g. heavy reliance on one country)\n"
            f"3. Search for recent supply chain disruptions or shortages\n"
            f"4. Identify single points of failure or key supplier dependencies\n"
            "Rate supply chain risk: LOW, MEDIUM, or HIGH and explain why."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()

        risk = "UNKNOWN"
        content = result.get("result", "").upper()
        for level in ["HIGH", "MEDIUM", "LOW"]:
            if f"SUPPLY CHAIN RISK: {level}" in content or f"SUPPLY CHAIN: {level}" in content:
                risk = level
                break

        return {
            "company": company_name,
            "supply_chain_risk": risk,
            "analysis": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


supply_chain_analysis_declaration = {
    "type": "function",
    "function": {
        "name": "supply_chain_analysis",
        "description": (
            "Analyze a company's supply chain dependencies and concentration risks. "
            "Identifies key suppliers, geographic risks, and single points of failure. "
            "Returns a SUPPLY_CHAIN_RISK level. Use in the analyze phase."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to analyze supply chain for"}
            },
            "required": ["company_name"]
        }
    }
}


def patent_search(company_name: str) -> dict:
    """Search for a company's patent portfolio and intellectual property position."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Patent search for: {company_name}")
        task = (
            f"Research the intellectual property and patent portfolio of {company_name}.\n"
            f"1. Search for '{company_name} patents intellectual property'\n"
            f"2. Find approximate number of patents and key technology areas\n"
            f"3. Search for any patent disputes, infringement cases, or licensing deals\n"
            "Summarize IP strength: STRONG, MODERATE, or WEAK, and note any IP risks."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()

        ip_strength = "UNKNOWN"
        content = result.get("result", "").upper()
        for label in ["STRONG", "MODERATE", "WEAK"]:
            if f"IP STRENGTH: {label}" in content or f"INTELLECTUAL PROPERTY: {label}" in content:
                ip_strength = label
                break

        return {
            "company": company_name,
            "ip_strength": ip_strength,
            "findings": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


patent_search_declaration = {
    "type": "function",
    "function": {
        "name": "patent_search",
        "description": (
            "Research a company's patent portfolio, intellectual property position, and any IP disputes. "
            "Returns an IP_STRENGTH rating (STRONG/MODERATE/WEAK). "
            "Use to assess defensibility of a company's technology advantages."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to search IP for"}
            },
            "required": ["company_name"]
        }
    }
}
