import re


def compare_financials(company_a: dict, company_b: dict) -> dict:
    """Side-by-side financial comparison of two companies."""
    try:
        metrics = ["revenue", "net_income", "total_debt", "total_equity",
                   "profit_margin_pct", "debt_to_equity", "market_cap"]
        table = []
        for m in metrics:
            val_a = company_a.get(m)
            val_b = company_b.get(m)
            if val_a is not None and val_b is not None:
                try:
                    better = company_a.get("name", "A") if float(val_a) > float(val_b) else company_b.get("name", "B")
                    if m in ("total_debt", "debt_to_equity"):
                        better = company_b.get("name", "B") if float(val_a) > float(val_b) else company_a.get("name", "A")
                except Exception:
                    better = "N/A"
                table.append({"metric": m, company_a.get("name", "Company A"): val_a,
                               company_b.get("name", "Company B"): val_b, "advantage": better})

        return {
            "comparison": table,
            "company_a": company_a.get("name", "Company A"),
            "company_b": company_b.get("name", "Company B"),
            "metrics_compared": len(table),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


compare_financials_declaration = {
    "type": "function",
    "function": {
        "name": "compare_financials",
        "description": (
            "Side-by-side financial comparison of two companies. "
            "Pass two dicts each with a 'name' key and financial metrics. "
            "Returns a table showing which company has the advantage on each metric. "
            "Use in the output phase when evaluating an acquisition target against a benchmark."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_a": {
                    "type": "object",
                    "description": "First company data dict with keys: name, revenue, net_income, total_debt, total_equity, etc."
                },
                "company_b": {
                    "type": "object",
                    "description": "Second company data dict with same structure as company_a"
                }
            },
            "required": ["company_a", "company_b"]
        }
    }
}


def extract_financial_data(text: str) -> dict:
    """Extract revenue, profit, debt and other financial figures from raw text."""
    try:
        billions = re.compile(r'\$\s*([\d,\.]+)\s*billion', re.IGNORECASE)
        millions = re.compile(r'\$\s*([\d,\.]+)\s*million', re.IGNORECASE)
        trillions = re.compile(r'\$\s*([\d,\.]+)\s*trillion', re.IGNORECASE)
        percentages = re.compile(r'([\d,\.]+)\s*%', re.IGNORECASE)

        def parse_num(s):
            return float(s.replace(",", ""))

        found_billions = [parse_num(m) * 1e9 for m in billions.findall(text)]
        found_millions = [parse_num(m) * 1e6 for m in millions.findall(text)]
        found_trillions = [parse_num(m) * 1e12 for m in trillions.findall(text)]
        found_pcts = [parse_num(m) for m in percentages.findall(text)]

        all_dollar_values = sorted(found_trillions + found_billions + found_millions, reverse=True)

        # Look for contextual keywords
        revenue_patterns = re.findall(r'revenue[^\$\n]{0,30}\$\s*([\d,\.]+)\s*(billion|million|trillion)', text, re.IGNORECASE)
        profit_patterns = re.findall(r'(?:net income|profit|earnings)[^\$\n]{0,30}\$\s*([\d,\.]+)\s*(billion|million|trillion)', text, re.IGNORECASE)
        debt_patterns = re.findall(r'(?:debt|liabilit)[^\$\n]{0,30}\$\s*([\d,\.]+)\s*(billion|million|trillion)', text, re.IGNORECASE)

        def scale(val, unit):
            multipliers = {"billion": 1e9, "million": 1e6, "trillion": 1e12}
            return parse_num(val) * multipliers.get(unit.lower(), 1)

        return {
            "extracted_revenue": scale(*revenue_patterns[0]) if revenue_patterns else None,
            "extracted_profit": scale(*profit_patterns[0]) if profit_patterns else None,
            "extracted_debt": scale(*debt_patterns[0]) if debt_patterns else None,
            "all_dollar_amounts_found": all_dollar_values[:10],
            "percentages_found": found_pcts[:10],
            "text_length": len(text),
            "note": "Values are extracted by pattern matching — verify against source."
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


extract_financial_data_declaration = {
    "type": "function",
    "function": {
        "name": "extract_financial_data",
        "description": (
            "Extract revenue, profit, debt, and other financial figures from raw scraped text. "
            "Finds dollar amounts (billions/millions) and percentages using pattern matching. "
            "Use this in the process phase after scraping a 10-K or financial news article."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Raw text from a financial filing, news article, or web page"}
            },
            "required": ["text"]
        }
    }
}
