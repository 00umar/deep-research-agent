import re
from loguru import logger


_LEGAL_KEYWORDS = [
    "lawsuit", "litigation", "sued", "class action", "settlement", "indictment",
    "investigation", "sec enforcement", "doj", "ftc", "antitrust", "fine", "penalty",
    "court order", "injunction", "arbitration", "complaint filed",
]
_FINANCIAL_RISK_KEYWORDS = [
    "going concern", "bankruptcy", "default", "debt covenant", "restructuring",
    "negative cash flow", "operating loss", "material weakness", "restatement",
    "impairment", "writedown", "goodwill impairment", "credit downgrade",
]
_GOVERNANCE_KEYWORDS = [
    "ceo departure", "cfo resignation", "board dispute", "insider selling",
    "whistleblower", "accounting fraud", "audit failure", "shareholder lawsuit",
    "proxy fight", "activist investor", "governance concern",
]
_OPERATIONAL_KEYWORDS = [
    "data breach", "cyberattack", "product recall", "supply chain disruption",
    "factory shutdown", "regulatory ban", "license revoked", "environmental violation",
]


def red_flag_scanner(data: str) -> dict:
    """Scan research text for financial, legal, governance, and operational red flags."""
    try:
        text_lower = data.lower()
        results = {
            "legal_flags": [],
            "financial_flags": [],
            "governance_flags": [],
            "operational_flags": [],
        }

        for kw in _LEGAL_KEYWORDS:
            if kw in text_lower:
                results["legal_flags"].append(kw)
        for kw in _FINANCIAL_RISK_KEYWORDS:
            if kw in text_lower:
                results["financial_flags"].append(kw)
        for kw in _GOVERNANCE_KEYWORDS:
            if kw in text_lower:
                results["governance_flags"].append(kw)
        for kw in _OPERATIONAL_KEYWORDS:
            if kw in text_lower:
                results["operational_flags"].append(kw)

        total_flags = sum(len(v) for v in results.values())
        severity = "LOW" if total_flags == 0 else ("MEDIUM" if total_flags <= 3 else "HIGH")

        return {
            **results,
            "total_flags": total_flags,
            "severity": severity,
            "recommendation": (
                "No immediate red flags detected." if total_flags == 0
                else f"Found {total_flags} red flag(s) across {sum(1 for v in results.values() if v)} categories. Investigate further."
            )
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


red_flag_scanner_declaration = {
    "type": "function",
    "function": {
        "name": "red_flag_scanner",
        "description": (
            "Scan research data for legal, financial, governance, and operational red flags. "
            "Detects keywords like 'lawsuit', 'going concern', 'data breach', 'ceo departure'. "
            "Returns categorized flags and a severity rating. "
            "Run this on all scraped text and news before writing the due diligence report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Combined research text to scan for red flags"}
            },
            "required": ["data"]
        }
    }
}


def risk_score_calculator(risk_factors: list) -> dict:
    """Compute an overall due diligence risk score from a list of identified risk factors."""
    try:
        if not risk_factors:
            return {"overall_score": 0, "risk_level": "LOW", "factors_evaluated": 0}

        severity_map = {
            "critical": 25, "high": 15, "medium": 8, "low": 3,
            "financial": 12, "legal": 15, "governance": 10, "operational": 8,
        }

        total_score = 0
        scored = []
        for factor in risk_factors:
            factor_lower = str(factor).lower()
            score = 3
            for keyword, pts in severity_map.items():
                if keyword in factor_lower:
                    score = max(score, pts)
            total_score += score
            scored.append({"factor": factor, "points": score})

        capped = min(total_score, 100)
        if capped >= 70:
            level = "CRITICAL"
        elif capped >= 45:
            level = "HIGH"
        elif capped >= 20:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "overall_score": capped,
            "risk_level": level,
            "scored_factors": scored,
            "factors_evaluated": len(risk_factors),
            "interpretation": f"Risk score {capped}/100 — {level} risk profile for due diligence purposes."
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


risk_score_calculator_declaration = {
    "type": "function",
    "function": {
        "name": "risk_score_calculator",
        "description": (
            "Compute an overall risk score (0-100) from a list of identified risk factors. "
            "Returns a risk level: LOW / MEDIUM / HIGH / CRITICAL. "
            "Use after running red_flag_scanner and litigation_search to quantify total risk exposure."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "risk_factors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of risk factors identified during research (e.g. 'pending class action lawsuit', 'high debt-to-equity')"
                }
            },
            "required": ["risk_factors"]
        }
    }
}


def litigation_search(company_name: str) -> dict:
    """Search for active lawsuits, legal investigations, and regulatory actions against a company."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Litigation search for: {company_name}")
        task = (
            f"Find all active or recent lawsuits, legal investigations, and regulatory actions involving {company_name}.\n"
            "1. Search for '{company_name} lawsuit 2024 2025'\n"
            "2. Search for '{company_name} SEC investigation OR FTC OR DOJ'\n"
            "3. Search for '{company_name} class action settlement'\n"
            "List each case with: type (lawsuit/investigation/settlement), status, and financial exposure if known.\n"
            "End with: LITIGATION_RISK: LOW, MEDIUM, or HIGH"
        ).replace("{company_name}", company_name)

        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()

        risk = "UNKNOWN"
        content = result.get("result", "").upper()
        for level in ["HIGH", "MEDIUM", "LOW"]:
            if f"LITIGATION_RISK: {level}" in content:
                risk = level
                break

        return {
            "company": company_name,
            "litigation_risk": risk,
            "findings": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


litigation_search_declaration = {
    "type": "function",
    "function": {
        "name": "litigation_search",
        "description": (
            "Search for active lawsuits, SEC investigations, FTC actions, and regulatory penalties against a company. "
            "Returns a LITIGATION_RISK level (LOW/MEDIUM/HIGH) with specific case details. "
            "Critical for any acquisition or investment due diligence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company to search litigation for (e.g. 'Apple Inc')"}
            },
            "required": ["company_name"]
        }
    }
}
