"""
Integration test for tools/finance/sec_filings.py.

Makes a real HTTP request to the public SEC EDGAR API — no API key required.
Run with: pytest -m integration
Skip in offline/CI environments with: pytest -m "not integration"
"""
import pytest
from tools.finance.sec_filings import sec_search

pytestmark = pytest.mark.integration


class TestSecSearchIntegration:
    def test_apple_returns_filings(self):
        result = sec_search("Apple Inc", filing_type="10-K")
        assert "error" not in result, f"SEC search errored: {result}"
        assert result["total_found"] > 0
        assert len(result["filings"]) > 0

    def test_filing_has_expected_fields(self):
        result = sec_search("Apple Inc", filing_type="10-K")
        assert "error" not in result
        filing = result["filings"][0]
        for field in ("company", "form", "filed", "accession"):
            assert field in filing, f"Missing field: {field}"

    def test_filing_type_is_10k(self):
        result = sec_search("Apple Inc", filing_type="10-K")
        assert "error" not in result
        for filing in result["filings"]:
            assert "10-K" in filing["form"]

    def test_nonexistent_company_returns_zero_filings(self):
        result = sec_search("ZZZZNONEXISTENTCOMPANYXYZ1234567890")
        assert "error" not in result
        assert result["total_found"] == 0
        assert result["filings"] == []
