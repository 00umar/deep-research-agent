"""Unit tests for tools/risk/scanner.py — pure keyword matching, no API calls."""
import pytest
from tools.risk.scanner import red_flag_scanner, risk_score_calculator


class TestRedFlagScanner:
    def test_detects_legal_flag(self):
        result = red_flag_scanner("The company faces a class action lawsuit filed in federal court.")
        assert "lawsuit" in result["legal_flags"] or "class action" in result["legal_flags"]
        assert result["total_flags"] >= 1

    def test_detects_financial_flag(self):
        result = red_flag_scanner("Auditors issued a going concern warning and noted the material weakness.")
        assert result["total_flags"] >= 1
        assert len(result["financial_flags"]) >= 1

    def test_detects_governance_flag(self):
        result = red_flag_scanner("The CEO departure was followed by a whistleblower complaint.")
        assert result["total_flags"] >= 1
        assert len(result["governance_flags"]) >= 1

    def test_clean_text_has_no_flags(self):
        result = red_flag_scanner("Apple reported strong quarterly earnings with solid revenue growth.")
        assert result["total_flags"] == 0
        assert result["severity"] == "LOW"

    def test_severity_escalates_with_flag_count(self):
        bad_text = (
            "lawsuit investigation fine settlement bankruptcy restructuring "
            "ceo departure whistleblower data breach"
        )
        result = red_flag_scanner(bad_text)
        assert result["severity"] in ("MEDIUM", "HIGH")

    def test_result_has_required_keys(self):
        result = red_flag_scanner("text")
        for key in ("legal_flags", "financial_flags", "governance_flags", "operational_flags",
                    "total_flags", "severity", "recommendation"):
            assert key in result


class TestRiskScoreCalculator:
    def test_empty_factors_returns_low_risk(self):
        result = risk_score_calculator([])
        assert result["risk_level"] == "LOW"
        assert result["overall_score"] == 0

    def test_high_severity_factors_raise_score(self):
        factors = ["Active legal investigation by DOJ", "Critical financial covenant breach",
                   "High debt-to-equity ratio"]
        result = risk_score_calculator(factors)
        assert result["overall_score"] > 0
        assert result["risk_level"] in ("MEDIUM", "HIGH", "CRITICAL")

    def test_score_capped_at_100(self):
        many_critical = [f"critical financial fraud case {i}" for i in range(20)]
        result = risk_score_calculator(many_critical)
        assert result["overall_score"] <= 100

    def test_scored_factors_count_matches_input(self):
        factors = ["risk A", "risk B", "risk C"]
        result = risk_score_calculator(factors)
        assert result["factors_evaluated"] == 3
        assert len(result["scored_factors"]) == 3

    def test_result_has_required_keys(self):
        result = risk_score_calculator(["some risk"])
        for key in ("overall_score", "risk_level", "scored_factors", "factors_evaluated"):
            assert key in result
