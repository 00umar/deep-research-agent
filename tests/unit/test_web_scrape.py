"""Unit tests for tools/web/scrape.py — httpx is mocked so no real network calls."""
import pytest
from unittest.mock import patch, MagicMock
from tools.web.scrape import web_scrape

FAKE_HTML = """
<html>
  <head><title>Acme Corp Investor Relations</title></head>
  <body>
    <header>Nav</header>
    <main>
      <p>Acme Corp reported revenue of $10 billion and net income of $2 billion for fiscal 2024.</p>
      <p>The company operates in 50 countries with 80,000 employees.</p>
    </main>
    <script>console.log('ignored')</script>
    <footer>Footer text</footer>
  </body>
</html>
"""


def _mock_response(status_code=200, text=FAKE_HTML):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        from httpx import HTTPStatusError, Request, Response
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


class TestWebScrape:
    @patch("tools.web.scrape.httpx.get")
    def test_returns_title_from_html(self, mock_get):
        mock_get.return_value = _mock_response()
        result = web_scrape("https://example.com/investors")
        assert result["title"] == "Acme Corp Investor Relations"

    @patch("tools.web.scrape.httpx.get")
    def test_returns_content_without_script_or_footer(self, mock_get):
        mock_get.return_value = _mock_response()
        result = web_scrape("https://example.com/investors")
        assert "console.log" not in result["content"]
        assert "revenue" in result["content"]

    @patch("tools.web.scrape.httpx.get")
    def test_result_has_required_keys(self, mock_get):
        mock_get.return_value = _mock_response()
        result = web_scrape("https://example.com")
        for key in ("url", "title", "content", "word_count"):
            assert key in result

    @patch("tools.web.scrape.httpx.get")
    def test_content_capped_at_8000_chars(self, mock_get):
        # Large page should be truncated
        large_html = "<html><body>" + ("word " * 5000) + "</body></html>"
        mock_get.return_value = _mock_response(text=large_html)
        result = web_scrape("https://example.com/long")
        assert len(result["content"]) <= 8000

    @patch("tools.web.scrape.httpx.get")
    def test_uses_chrome_user_agent(self, mock_get):
        mock_get.return_value = _mock_response()
        web_scrape("https://example.com")
        call_kwargs = mock_get.call_args
        headers = call_kwargs.kwargs.get("headers", {})
        assert "Chrome" in headers.get("User-Agent", "")

    @patch("tools.web.scrape.httpx.get")
    def test_http_error_returns_error_dict(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        result = web_scrape("https://example.com/blocked")
        assert "error" in result
