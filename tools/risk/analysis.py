def swot_generator(strengths: list, weaknesses: list,
                    opportunities: list, threats: list,
                    company_name: str = "Company") -> dict:
    """Format a structured SWOT analysis from research findings."""
    try:
        def fmt(items):
            return [str(i).strip() for i in items if str(i).strip()]

        s = fmt(strengths)
        w = fmt(weaknesses)
        o = fmt(opportunities)
        t = fmt(threats)

        score = (len(s) + len(o)) - (len(w) + len(t))
        if score > 2:
            verdict = "FAVORABLE — strengths and opportunities outweigh risks"
        elif score < -2:
            verdict = "UNFAVORABLE — weaknesses and threats are dominant concerns"
        else:
            verdict = "MIXED — balanced risk/opportunity profile, proceed with caution"

        markdown = f"""## SWOT Analysis: {company_name}

### Strengths
{chr(10).join(f'- {s_}' for s_ in s) or '- None identified'}

### Weaknesses
{chr(10).join(f'- {w_}' for w_ in w) or '- None identified'}

### Opportunities
{chr(10).join(f'- {o_}' for o_ in o) or '- None identified'}

### Threats
{chr(10).join(f'- {t_}' for t_ in t) or '- None identified'}

**Overall Verdict:** {verdict}"""

        return {
            "company": company_name,
            "strengths": s,
            "weaknesses": w,
            "opportunities": o,
            "threats": t,
            "net_score": score,
            "verdict": verdict,
            "markdown": markdown,
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


swot_generator_declaration = {
    "type": "function",
    "function": {
        "name": "swot_generator",
        "description": (
            "Generate a structured SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) "
            "from research findings. Returns formatted markdown and an overall verdict. "
            "Use in the output phase after completing research."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company being analyzed"},
                "strengths": {"type": "array", "items": {"type": "string"}, "description": "List of company strengths"},
                "weaknesses": {"type": "array", "items": {"type": "string"}, "description": "List of company weaknesses"},
                "opportunities": {"type": "array", "items": {"type": "string"}, "description": "List of market opportunities"},
                "threats": {"type": "array", "items": {"type": "string"}, "description": "List of threats and risks"}
            },
            "required": ["strengths", "weaknesses", "opportunities", "threats"]
        }
    }
}


def risk_impact_matrix(risks: list) -> dict:
    """Build a risk matrix mapping each risk by likelihood and impact."""
    try:
        if not risks:
            return {"error": "NoRisks", "message": "Provide at least one risk"}

        _IMPACT_KEYWORDS = {
            "high": ["bankrupt", "fraud", "criminal", "collapse", "lawsuit", "billion", "critical", "severe", "major"],
            "low": ["minor", "small", "unlikely", "remote", "negligible", "slight"],
        }
        _LIKELIHOOD_KEYWORDS = {
            "high": ["ongoing", "active", "current", "confirmed", "pending", "known", "existing"],
            "low": ["potential", "possible", "hypothetical", "if", "may", "could"],
        }

        matrix = []
        for risk in risks:
            risk_lower = str(risk).lower()

            impact = "MEDIUM"
            for kw in _IMPACT_KEYWORDS["high"]:
                if kw in risk_lower:
                    impact = "HIGH"
                    break
            if impact == "MEDIUM":
                for kw in _IMPACT_KEYWORDS["low"]:
                    if kw in risk_lower:
                        impact = "LOW"
                        break

            likelihood = "MEDIUM"
            for kw in _LIKELIHOOD_KEYWORDS["high"]:
                if kw in risk_lower:
                    likelihood = "HIGH"
                    break
            if likelihood == "MEDIUM":
                for kw in _LIKELIHOOD_KEYWORDS["low"]:
                    if kw in risk_lower:
                        likelihood = "LOW"
                        break

            priority = "MONITOR"
            if impact == "HIGH" and likelihood == "HIGH":
                priority = "CRITICAL — address immediately"
            elif impact == "HIGH" or likelihood == "HIGH":
                priority = "HIGH PRIORITY — mitigate before proceeding"
            elif impact == "LOW" and likelihood == "LOW":
                priority = "LOW — acceptable"

            matrix.append({
                "risk": risk,
                "likelihood": likelihood,
                "impact": impact,
                "priority": priority,
            })

        matrix.sort(key=lambda x: (
            {"CRITICAL — address immediately": 0, "HIGH PRIORITY — mitigate before proceeding": 1,
             "MONITOR": 2, "LOW — acceptable": 3}.get(x["priority"], 2)
        ))

        critical_count = sum(1 for r in matrix if "CRITICAL" in r["priority"])
        high_count = sum(1 for r in matrix if "HIGH PRIORITY" in r["priority"])

        return {
            "risk_matrix": matrix,
            "total_risks": len(matrix),
            "critical_risks": critical_count,
            "high_priority_risks": high_count,
            "summary": f"{critical_count} critical, {high_count} high-priority risks identified out of {len(matrix)} total."
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


risk_impact_matrix_declaration = {
    "type": "function",
    "function": {
        "name": "risk_impact_matrix",
        "description": (
            "Build a risk impact vs. likelihood matrix from a list of identified risks. "
            "Classifies each risk as CRITICAL, HIGH PRIORITY, MONITOR, or LOW. "
            "Use in the output phase to structure the risk section of the due diligence report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "risks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of risk descriptions to map (e.g. 'Active antitrust investigation by FTC')"
                }
            },
            "required": ["risks"]
        }
    }
}


def competitive_landscape(company_name: str, sector: str) -> dict:
    """Research a company's main competitors and market positioning."""
    try:
        from agent.subagent import SubAgent
        from loguru import logger
        logger.info(f"Competitive landscape for: {company_name} in {sector}")
        task = (
            f"Research the competitive landscape for {company_name} in the {sector} sector.\n"
            f"1. Search for '{company_name} competitors {sector}'\n"
            f"2. Find the top 3-5 direct competitors and their market positions\n"
            f"3. Identify {company_name}'s key competitive advantages and disadvantages\n"
            "Summarize: who are the top competitors, what is this company's market position, "
            "and what competitive risks exist?"
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "web_scrape", "text_summarize"])
        result = agent.run()
        return {
            "company": company_name,
            "sector": sector,
            "analysis": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


competitive_landscape_declaration = {
    "type": "function",
    "function": {
        "name": "competitive_landscape",
        "description": (
            "Research a company's main competitors and competitive positioning in its sector. "
            "Identifies top rivals, market shares, and competitive advantages/disadvantages. "
            "Use in the analyze phase to understand the company's market position."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to analyze"},
                "sector": {"type": "string", "description": "Industry sector (e.g. 'cloud computing', 'electric vehicles')"}
            },
            "required": ["company_name", "sector"]
        }
    }
}
