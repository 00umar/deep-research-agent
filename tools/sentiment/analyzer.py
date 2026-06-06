import re
from loguru import logger


_POSITIVE = {
    "growth", "profit", "revenue", "increased", "strong", "beat", "exceeded",
    "expanded", "gained", "improved", "positive", "success", "record", "outperform",
    "momentum", "opportunity", "innovative", "leading", "robust", "surge", "soar",
    "milestone", "breakthrough", "confident", "optimistic", "recovery", "demand",
}
_NEGATIVE = {
    "loss", "decline", "decreased", "lawsuit", "investigation", "fell", "missed",
    "reduced", "risk", "concern", "poor", "failed", "debt", "layoffs", "fraud",
    "penalty", "fine", "violation", "bankruptcy", "restructuring", "writedown",
    "warning", "uncertainty", "headwind", "pressure", "weak", "disappointing",
    "recall", "breach", "downgrade", "cut", "miss", "shortfall",
}
_HEDGE_WORDS = {
    "may", "might", "could", "possibly", "potentially", "approximately", "subject to",
    "if", "assuming", "expect to", "intend to", "believe", "estimate", "forward-looking",
}
_CONFIDENT_WORDS = {
    "will", "committed", "certain", "confident", "guaranteed", "definitive",
    "clearly", "demonstrated", "proven", "delivered", "achieved",
}


def score_sentiment(text: str) -> dict:
    """Score the sentiment of a text as positive, negative, or neutral."""
    try:
        words = re.findall(r'\b\w+\b', text.lower())
        word_set = set(words)

        pos_hits = [w for w in words if w in _POSITIVE]
        neg_hits = [w for w in words if w in _NEGATIVE]

        score = len(pos_hits) - len(neg_hits)
        total = len(pos_hits) + len(neg_hits)
        ratio = round(score / total, 2) if total else 0

        if ratio > 0.2:
            label = "POSITIVE"
        elif ratio < -0.2:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

        return {
            "sentiment": label,
            "score": score,
            "ratio": ratio,
            "positive_signals": list(set(pos_hits))[:10],
            "negative_signals": list(set(neg_hits))[:10],
            "word_count": len(words),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


score_sentiment_declaration = {
    "type": "function",
    "function": {
        "name": "score_sentiment",
        "description": (
            "Score the sentiment of a text as POSITIVE, NEGATIVE, or NEUTRAL using financial keyword analysis. "
            "Returns a numeric score and the specific words driving the sentiment. "
            "Use on news articles, earnings transcripts, or any text gathered during research."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze for sentiment"}
            },
            "required": ["text"]
        }
    }
}


def aggregate_sentiment(texts: list) -> dict:
    """Aggregate sentiment across multiple news items or sources."""
    try:
        if not texts:
            return {"error": "NoTexts", "message": "Provide at least one text to analyze"}

        scores = []
        labels = []
        for t in texts:
            result = score_sentiment(t)
            if "error" not in result:
                scores.append(result["score"])
                labels.append(result["sentiment"])

        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        pos_count = labels.count("POSITIVE")
        neg_count = labels.count("NEGATIVE")
        neu_count = labels.count("NEUTRAL")

        overall = "POSITIVE" if avg_score > 0.5 else ("NEGATIVE" if avg_score < -0.5 else "NEUTRAL")

        return {
            "overall_sentiment": overall,
            "average_score": avg_score,
            "positive_count": pos_count,
            "negative_count": neg_count,
            "neutral_count": neu_count,
            "sources_analyzed": len(texts),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


aggregate_sentiment_declaration = {
    "type": "function",
    "function": {
        "name": "aggregate_sentiment",
        "description": (
            "Aggregate sentiment across multiple news items, articles, or text sources. "
            "Returns an overall sentiment label and a breakdown of positive/negative/neutral counts. "
            "Use after collecting multiple news articles about a company."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "texts": {"type": "array", "items": {"type": "string"},
                          "description": "List of text strings to analyze"}
            },
            "required": ["texts"]
        }
    }
}


def detect_hedging_language(text: str) -> dict:
    """Detect cautious or evasive language in executive statements and filings."""
    try:
        text_lower = text.lower()
        hedge_hits = [w for w in _HEDGE_WORDS if w in text_lower]
        conf_hits = [w for w in _CONFIDENT_WORDS if w in text_lower]

        hedge_ratio = len(hedge_hits) / max(len(hedge_hits) + len(conf_hits), 1)

        if hedge_ratio > 0.6:
            tone = "CAUTIOUS — executives using many hedging phrases, may signal uncertainty"
        elif hedge_ratio < 0.3:
            tone = "CONFIDENT — direct language, management expressing certainty"
        else:
            tone = "BALANCED — mix of cautious and confident language"

        return {
            "tone": tone,
            "hedge_ratio": round(hedge_ratio, 2),
            "hedging_phrases_found": hedge_hits,
            "confident_phrases_found": conf_hits,
            "interpretation": (
                "High hedging in earnings calls or annual reports can signal management uncertainty "
                "about future performance. Compare across years to detect tone shifts."
            )
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


detect_hedging_language_declaration = {
    "type": "function",
    "function": {
        "name": "detect_hedging_language",
        "description": (
            "Detect cautious, evasive, or hedging language in executive statements, earnings calls, or filings. "
            "High hedging may signal management uncertainty or attempt to soften bad news. "
            "Use on scraped earnings call transcripts or CEO letters."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Executive statement, earnings call transcript, or filing text"}
            },
            "required": ["text"]
        }
    }
}


def market_mood(sector: str) -> dict:
    """Research current market sentiment for a sector using live web search."""
    try:
        from agent.subagent import SubAgent
        logger.info(f"Checking market mood for sector: {sector}")
        task = (
            f"Research the current market sentiment and investor mood for the {sector} sector.\n"
            "1. Search for recent analyst opinions and market outlooks\n"
            "2. Search for any major headwinds or tailwinds affecting the sector\n"
            "3. Find whether institutional investors are bullish or bearish\n"
            "Summarize: overall mood (BULLISH/BEARISH/MIXED), key drivers, and 2-3 specific data points."
        )
        agent = SubAgent(task=task, allowed_tools=["web_search", "news_search", "text_summarize"])
        result = agent.run()

        mood = "MIXED"
        content = result.get("result", "").upper()
        if "BULLISH" in content and "BEARISH" not in content:
            mood = "BULLISH"
        elif "BEARISH" in content and "BULLISH" not in content:
            mood = "BEARISH"

        return {
            "sector": sector,
            "overall_mood": mood,
            "analysis": result.get("result", ""),
            "tool_calls_made": result.get("tool_calls_made", 0),
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e), "sector": sector}


market_mood_declaration = {
    "type": "function",
    "function": {
        "name": "market_mood",
        "description": (
            "Research current market sentiment for a specific sector (e.g. 'technology', 'healthcare', 'fintech'). "
            "Returns BULLISH/BEARISH/MIXED assessment with supporting evidence from live web research. "
            "Use in the analyze phase to contextualize a company's performance against its sector."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sector": {"type": "string", "description": "Market sector to assess (e.g. 'cloud computing', 'electric vehicles', 'banking')"}
            },
            "required": ["sector"]
        }
    }
}
