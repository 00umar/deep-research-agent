import httpx
from loguru import logger


def sec_search(company_name: str, filing_type: str = "10-K") -> dict:
    """Search SEC EDGAR for company filings."""
    try:
        url = "https://efts.sec.gov/LATEST/search-index"
        params = {"q": f'"{company_name}"', "forms": filing_type, "dateRange": "custom",
                  "startdt": "2022-01-01", "enddt": "2026-12-31"}
        resp = httpx.get(url, params=params, timeout=15,
                         headers={"User-Agent": "DueDiligenceAgent research@example.com"})
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        filings = []
        for h in hits[:5]:
            src = h.get("_source", {})
            filings.append({
                "company": src.get("entity_name", company_name),
                "form": src.get("form_type", filing_type),
                "filed": src.get("file_date", ""),
                "period": src.get("period_of_report", ""),
                "accession": src.get("accession_no", ""),
            })
        return {
            "company": company_name,
            "filing_type": filing_type,
            "total_found": data.get("hits", {}).get("total", {}).get("value", 0),
            "filings": filings,
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


sec_search_declaration = {
    "type": "function",
    "function": {
        "name": "sec_search",
        "description": (
            "Search SEC EDGAR for a company's regulatory filings (10-K annual reports, 10-Q quarterlies, 8-K events). "
            "Returns filing dates, periods covered, and accession numbers. "
            "Use this early in due diligence to confirm the company is publicly listed and find recent filings."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company name to search for (e.g. 'Apple Inc')"},
                "filing_type": {"type": "string", "description": "SEC form type: 10-K, 10-Q, 8-K, DEF 14A (default: 10-K)"}
            },
            "required": ["company_name"]
        }
    }
}


def fetch_10k_summary(company_name: str) -> dict:
    """Fetch key sections from the most recent 10-K annual report via SEC EDGAR full-text search."""
    try:
        url = "https://efts.sec.gov/LATEST/search-index"
        params = {"q": f'"{company_name}"', "forms": "10-K"}
        resp = httpx.get(url, params=params, timeout=15,
                         headers={"User-Agent": "DueDiligenceAgent research@example.com"})
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            return {"error": "NoFilingsFound", "message": f"No 10-K found for {company_name} on SEC EDGAR", "company": company_name}

        latest = hits[0].get("_source", {})
        accession = latest.get("accession_no", "").replace("-", "")
        cik = latest.get("cik", "")
        file_date = latest.get("file_date", "")
        period = latest.get("period_of_report", "")

        # Build EDGAR viewer URL for reference
        edgar_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=5"

        return {
            "company": latest.get("entity_name", company_name),
            "cik": cik,
            "latest_10k_filed": file_date,
            "period_covered": period,
            "accession_number": latest.get("accession_no", ""),
            "edgar_filings_url": edgar_url,
            "note": "Use web_scrape on the edgar_filings_url to read the actual 10-K document content.",
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "company": company_name}


fetch_10k_summary_declaration = {
    "type": "function",
    "function": {
        "name": "fetch_10k_summary",
        "description": (
            "Fetch the most recent 10-K annual report metadata for a company from SEC EDGAR. "
            "Returns the filing date, period covered, CIK, and a URL to access the full document. "
            "Use this to find where the 10-K is so you can scrape it for financial details."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Company name exactly as registered with SEC (e.g. 'Apple Inc', 'Microsoft Corporation')"}
            },
            "required": ["company_name"]
        }
    }
}
