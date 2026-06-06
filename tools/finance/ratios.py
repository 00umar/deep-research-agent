def financial_ratios(revenue: float, net_income: float, total_debt: float,
                     total_equity: float, current_assets: float = 0,
                     current_liabilities: float = 0) -> dict:
    """Calculate key financial ratios from raw numbers."""
    try:
        results = {"inputs": {
            "revenue": revenue, "net_income": net_income,
            "total_debt": total_debt, "total_equity": total_equity
        }}

        # Profitability
        results["profit_margin_pct"] = round((net_income / revenue) * 100, 2) if revenue else None
        results["return_on_equity_pct"] = round((net_income / total_equity) * 100, 2) if total_equity else None

        # Leverage
        results["debt_to_equity"] = round(total_debt / total_equity, 2) if total_equity else None
        results["debt_to_revenue"] = round(total_debt / revenue, 2) if revenue else None

        # Liquidity
        if current_assets and current_liabilities:
            results["current_ratio"] = round(current_assets / current_liabilities, 2)
        else:
            results["current_ratio"] = None

        # Risk flags
        flags = []
        if results["profit_margin_pct"] is not None and results["profit_margin_pct"] < 0:
            flags.append("NEGATIVE PROFIT MARGIN — company is losing money")
        if results["debt_to_equity"] is not None and results["debt_to_equity"] > 2:
            flags.append("HIGH DEBT-TO-EQUITY (>2x) — heavy leverage risk")
        if results["current_ratio"] is not None and results["current_ratio"] < 1:
            flags.append("CURRENT RATIO BELOW 1 — may struggle to meet short-term obligations")

        results["risk_flags"] = flags
        results["flag_count"] = len(flags)
        return results
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


financial_ratios_declaration = {
    "type": "function",
    "function": {
        "name": "financial_ratios",
        "description": (
            "Calculate key financial ratios: profit margin, return on equity, debt-to-equity, current ratio. "
            "Automatically flags dangerous ratios (negative margins, excess leverage). "
            "Input the raw numbers you found from SEC filings or web research."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "revenue": {"type": "number", "description": "Annual revenue in dollars"},
                "net_income": {"type": "number", "description": "Net income (can be negative for losses)"},
                "total_debt": {"type": "number", "description": "Total debt obligations"},
                "total_equity": {"type": "number", "description": "Total shareholders equity"},
                "current_assets": {"type": "number", "description": "Current assets (optional, for liquidity ratio)"},
                "current_liabilities": {"type": "number", "description": "Current liabilities (optional, for liquidity ratio)"}
            },
            "required": ["revenue", "net_income", "total_debt", "total_equity"]
        }
    }
}


def dcf_valuation(free_cash_flows: list, growth_rate: float, discount_rate: float,
                  terminal_growth_rate: float = 0.03) -> dict:
    """Simple DCF valuation — estimates intrinsic value from projected cash flows."""
    try:
        if not free_cash_flows:
            return {"error": "NoCashFlows", "message": "Provide at least one year of free cash flow"}

        pv_cash_flows = []
        for i, fcf in enumerate(free_cash_flows, 1):
            projected = fcf * ((1 + growth_rate) ** i)
            pv = projected / ((1 + discount_rate) ** i)
            pv_cash_flows.append(round(pv, 0))

        terminal_value = (free_cash_flows[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        pv_terminal = terminal_value / ((1 + discount_rate) ** len(free_cash_flows))

        intrinsic_value = sum(pv_cash_flows) + pv_terminal

        return {
            "inputs": {
                "cash_flows": free_cash_flows,
                "growth_rate_pct": round(growth_rate * 100, 1),
                "discount_rate_pct": round(discount_rate * 100, 1),
                "terminal_growth_rate_pct": round(terminal_growth_rate * 100, 1),
            },
            "pv_of_projected_flows": pv_cash_flows,
            "terminal_value": round(pv_terminal, 0),
            "estimated_intrinsic_value": round(intrinsic_value, 0),
            "note": "Simplified DCF. Use as directional estimate, not precise valuation."
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


dcf_valuation_declaration = {
    "type": "function",
    "function": {
        "name": "dcf_valuation",
        "description": (
            "Run a discounted cash flow (DCF) model to estimate a company's intrinsic value. "
            "Provide historical free cash flows, an expected growth rate, and a discount rate. "
            "Use in the output phase after gathering financial data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "free_cash_flows": {"type": "array", "items": {"type": "number"},
                                    "description": "List of annual free cash flows (most recent first, in dollars)"},
                "growth_rate": {"type": "number", "description": "Expected annual growth rate as decimal (e.g. 0.08 for 8%)"},
                "discount_rate": {"type": "number", "description": "Discount/hurdle rate as decimal (e.g. 0.10 for 10%)"},
                "terminal_growth_rate": {"type": "number", "description": "Long-run terminal growth rate (default 0.03 = 3%)"}
            },
            "required": ["free_cash_flows", "growth_rate", "discount_rate"]
        }
    }
}


def revenue_trend(revenue_history: list, years: list = None) -> dict:
    """Analyze a company's revenue growth trend from historical data."""
    try:
        if len(revenue_history) < 2:
            return {"error": "InsufficientData", "message": "Need at least 2 years of revenue data"}

        changes = []
        for i in range(1, len(revenue_history)):
            prev = revenue_history[i - 1]
            curr = revenue_history[i]
            if prev and prev != 0:
                pct = round(((curr - prev) / abs(prev)) * 100, 1)
                changes.append(pct)

        avg_growth = round(sum(changes) / len(changes), 1) if changes else 0
        is_accelerating = len(changes) >= 2 and changes[-1] > changes[0]
        declining_years = sum(1 for c in changes if c < 0)

        flags = []
        if avg_growth < 0:
            flags.append("NEGATIVE AVERAGE REVENUE GROWTH — shrinking business")
        if declining_years >= 2:
            flags.append(f"REVENUE DECLINED IN {declining_years} PERIODS — inconsistent performance")
        if avg_growth > 30:
            flags.append("VERY HIGH GROWTH (>30%) — verify sustainability")

        return {
            "revenue_history": revenue_history,
            "years": years or list(range(len(revenue_history))),
            "yoy_growth_pct": changes,
            "average_growth_pct": avg_growth,
            "is_accelerating": is_accelerating,
            "declining_periods": declining_years,
            "risk_flags": flags,
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


revenue_trend_declaration = {
    "type": "function",
    "function": {
        "name": "revenue_trend",
        "description": (
            "Analyze a company's revenue growth trend from historical annual figures. "
            "Calculates year-over-year growth rates, average growth, and flags declining or inconsistent patterns. "
            "Input revenue numbers you found from SEC filings or financial news."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "revenue_history": {"type": "array", "items": {"type": "number"},
                                    "description": "Annual revenue values in order from oldest to newest"},
                "years": {"type": "array", "items": {"type": "string"},
                          "description": "Optional year labels matching the revenue values"}
            },
            "required": ["revenue_history"]
        }
    }
}


def debt_risk_analysis(total_debt: float, total_equity: float, ebitda: float,
                        interest_expense: float = 0, cash: float = 0) -> dict:
    """Assess a company's debt risk and repayment capacity."""
    try:
        results = {}

        results["debt_to_equity"] = round(total_debt / total_equity, 2) if total_equity else None
        results["debt_to_ebitda"] = round(total_debt / ebitda, 2) if ebitda else None
        results["net_debt"] = round(total_debt - cash, 0) if cash else total_debt
        results["interest_coverage"] = round(ebitda / interest_expense, 2) if interest_expense else None

        risk_level = "LOW"
        flags = []

        dte = results["debt_to_equity"]
        dteb = results["debt_to_ebitda"]
        ic = results["interest_coverage"]

        if dte and dte > 3:
            flags.append(f"SEVERE LEVERAGE — debt is {dte}x equity")
            risk_level = "HIGH"
        elif dte and dte > 1.5:
            flags.append(f"ELEVATED LEVERAGE — debt is {dte}x equity")
            if risk_level == "LOW":
                risk_level = "MEDIUM"

        if dteb and dteb > 5:
            flags.append(f"DEBT/EBITDA > 5x — will take 5+ years of earnings to repay debt")
            risk_level = "HIGH"
        elif dteb and dteb > 3:
            flags.append(f"DEBT/EBITDA > 3x — moderate repayment pressure")
            if risk_level == "LOW":
                risk_level = "MEDIUM"

        if ic and ic < 2:
            flags.append("INTEREST COVERAGE < 2x — earnings barely cover interest payments")
            risk_level = "HIGH"

        results["overall_debt_risk"] = risk_level
        results["risk_flags"] = flags
        return results
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


debt_risk_analysis_declaration = {
    "type": "function",
    "function": {
        "name": "debt_risk_analysis",
        "description": (
            "Assess a company's debt burden and repayment capacity. "
            "Calculates debt-to-EBITDA, interest coverage ratio, and net debt. "
            "Returns an overall risk level (LOW/MEDIUM/HIGH) with specific flags. "
            "Use in the analyze phase after gathering financial figures."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "total_debt": {"type": "number", "description": "Total debt in dollars"},
                "total_equity": {"type": "number", "description": "Total shareholders equity"},
                "ebitda": {"type": "number", "description": "Earnings before interest, taxes, depreciation and amortization"},
                "interest_expense": {"type": "number", "description": "Annual interest expense (optional)"},
                "cash": {"type": "number", "description": "Cash and equivalents on hand (optional, for net debt)"}
            },
            "required": ["total_debt", "total_equity", "ebitda"]
        }
    }
}
