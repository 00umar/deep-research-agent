"""Unit tests for tools/risk/analysis.py — swot_generator and risk_impact_matrix."""
import pytest
from tools.risk.analysis import swot_generator, risk_impact_matrix


class TestSwotGenerator:
    def test_strengths_dominant_returns_favorable_verdict(self):
        result = swot_generator(
            strengths=["market leader", "strong cash flow", "brand recognition", "global scale"],
            weaknesses=["high costs"],
            opportunities=["AI expansion", "emerging markets"],
            threats=["competition"],
            company_name="TestCo",
        )
        assert "FAVORABLE" in result["verdict"]
        assert result["net_score"] > 2

    def test_weaknesses_dominant_returns_unfavorable_verdict(self):
        result = swot_generator(
            strengths=["one strength"],
            weaknesses=["debt", "regulatory issues", "declining revenue", "talent loss"],
            opportunities=[],
            threats=["new entrant", "price war", "regulation"],
            company_name="TestCo",
        )
        assert "UNFAVORABLE" in result["verdict"]
        assert result["net_score"] < -2

    def test_balanced_returns_mixed_verdict(self):
        result = swot_generator(
            strengths=["strength A", "strength B"],
            weaknesses=["weakness A", "weakness B"],
            opportunities=["opp A"],
            threats=["threat A"],
        )
        assert "MIXED" in result["verdict"]

    def test_markdown_contains_section_headers(self):
        result = swot_generator(["s"], ["w"], ["o"], ["t"], "Acme")
        for header in ("### Strengths", "### Weaknesses", "### Opportunities", "### Threats"):
            assert header in result["markdown"]

    def test_empty_lists_do_not_crash(self):
        result = swot_generator([], [], [], [])
        assert "verdict" in result
        assert "markdown" in result


class TestRiskImpactMatrix:
    def test_active_lawsuit_flagged_high(self):
        result = risk_impact_matrix(["Active antitrust lawsuit pending in court"])
        assert result["total_risks"] == 1
        entry = result["risk_matrix"][0]
        assert entry["likelihood"] == "HIGH"

    def test_potential_risk_gets_lower_likelihood(self):
        result = risk_impact_matrix(["Potential currency risk if markets shift"])
        entry = result["risk_matrix"][0]
        assert entry["likelihood"] == "LOW"

    def test_critical_bankruptcy_risk_prioritized(self):
        result = risk_impact_matrix(["Ongoing bankruptcy proceedings active now"])
        entry = result["risk_matrix"][0]
        assert "CRITICAL" in entry["priority"] or "HIGH" in entry["priority"]

    def test_empty_list_returns_error(self):
        result = risk_impact_matrix([])
        assert "error" in result

    def test_multiple_risks_sorted_by_priority(self):
        risks = [
            "Potential minor regulatory filing delay",
            "Active confirmed fraud investigation — critical financial exposure",
        ]
        result = risk_impact_matrix(risks)
        assert result["total_risks"] == 2
        # Critical/high should come before low in sorted order
        priorities = [r["priority"] for r in result["risk_matrix"]]
        assert any("CRITICAL" in p or "HIGH" in p for p in priorities[:1])
