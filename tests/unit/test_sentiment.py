"""Unit tests for tools/sentiment/analyzer.py — pure keyword logic, no API calls."""
import pytest
from tools.sentiment.analyzer import score_sentiment, detect_hedging_language


class TestScoreSentiment:
    def test_positive_text_returns_positive_label(self):
        text = "Record revenue growth and strong profit momentum exceeded all expectations."
        result = score_sentiment(text)
        assert result["sentiment"] == "POSITIVE"
        assert result["score"] > 0

    def test_negative_text_returns_negative_label(self):
        text = "Massive loss and debt fuelled by lawsuit, investigation, and layoffs. Bankruptcy risk."
        result = score_sentiment(text)
        assert result["sentiment"] == "NEGATIVE"
        assert result["score"] < 0

    def test_empty_string_does_not_crash(self):
        result = score_sentiment("")
        assert "sentiment" in result
        assert result["sentiment"] == "NEUTRAL"

    def test_result_has_required_keys(self):
        result = score_sentiment("Some company text.")
        for key in ("sentiment", "score", "ratio", "positive_signals", "negative_signals", "word_count"):
            assert key in result

    def test_positive_signals_are_a_list(self):
        result = score_sentiment("Strong revenue growth and record profits.")
        assert isinstance(result["positive_signals"], list)

    def test_word_count_is_accurate(self):
        text = "one two three four five"
        result = score_sentiment(text)
        assert result["word_count"] == 5


class TestDetectHedgingLanguage:
    def test_hedging_heavy_text_returns_cautious_tone(self):
        text = "We may possibly see growth, but could potentially face headwinds if conditions change."
        result = detect_hedging_language(text)
        assert "CAUTIOUS" in result["tone"]

    def test_confident_text_returns_confident_tone(self):
        text = "We will deliver. Our results are certain and we have committed to clear targets. Proven approach."
        result = detect_hedging_language(text)
        assert "CONFIDENT" in result["tone"]

    def test_result_has_required_keys(self):
        result = detect_hedging_language("Some text.")
        for key in ("tone", "hedge_ratio", "hedging_phrases_found", "confident_phrases_found"):
            assert key in result

    def test_hedge_ratio_between_0_and_1(self):
        result = detect_hedging_language("We may grow.")
        assert 0.0 <= result["hedge_ratio"] <= 1.0
