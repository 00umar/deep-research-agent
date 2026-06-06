"""Smoke tests for individual tools — verify they return expected structure without crashing."""

import pytest
from tools.registry import ToolRegistry


@pytest.fixture(scope="module")
def registry():
    return ToolRegistry()


def test_registry_loads_tools(registry):
    assert registry.tool_count >= 50


def test_core_tool_names_present(registry):
    # Check that the essential due-diligence tools are registered.
    # Not exhaustive — use registry.tool_names to see the full list.
    required = {
        "web_search", "web_scrape", "news_search",
        "file_read", "file_write", "file_list", "file_exists",
        "text_summarize", "extract_keywords", "extract_entities",
        "compile_report", "generate_outline", "format_citations",
        "sec_search", "fetch_10k_summary",
        "score_sentiment", "detect_hedging_language",
        "red_flag_scanner", "risk_score_calculator",
        "swot_generator", "risk_impact_matrix",
        "financial_ratios", "revenue_trend", "debt_risk_analysis",
        "fact_check", "confidence_score",
    }
    registered = set(registry.tool_names)
    missing = required - registered
    assert not missing, f"Missing tools: {missing}"


def test_unknown_tool_returns_error(registry):
    result = registry.execute("nonexistent_tool", {})
    assert result["error"] == "ToolNotFound"


def test_text_clean_strips_html(registry):
    result = registry.execute("text_clean", {"text": "<p>Hello <b>world</b></p>"})
    assert "error" not in result
    cleaned = result.get("text") or result.get("cleaned", "")
    assert "<p>" not in cleaned
    assert "Hello" in cleaned


def test_format_citations_numbered(registry):
    sources = [{"title": "OpenAI Blog", "url": "https://openai.com/blog"}]
    result = registry.execute("format_citations", {"sources": sources})
    assert "error" not in result
    # accepts either a formatted_text string or a citations list containing "[1]"
    text = result.get("formatted_text") or str(result.get("citations", ""))
    assert "[1]" in text


def test_file_exists_missing_path(registry):
    result = registry.execute("file_exists", {"path": "outputs/this_file_does_not_exist_xyz.md"})
    assert result.get("exists") is False


def test_file_write_and_read(registry, tmp_path):
    test_path = str(tmp_path / "test_output.txt")
    write_result = registry.execute("file_write", {"path": test_path, "content": "hello test"})
    assert "error" not in write_result

    read_result = registry.execute("file_read", {"path": test_path})
    assert "error" not in read_result
    assert "hello test" in read_result.get("content", "")
