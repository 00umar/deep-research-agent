# Deep Research Agent

An autonomous corporate due diligence agent built for the X-ARC Agentic AI Engineer Hackathon.

Give it a company name. It researches SEC filings, news, financial data, and risk factors —
then produces a structured, cited report and scores it automatically.

## Demo

```
streamlit run app.py
```

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   GEMINI_API_KEY=...
   CEREBRAS_API_KEY=...
   GROQ_API_KEY=...
   ```
2. Install dependencies: `pip install -r requirements.txt`
3. Run the UI: `streamlit run app.py`
   Or run headless: `python main.py`

## Architecture

```
agent/
  core.py          — 5-phase agent loop (plan → gather → process → analyze → output)
  llm_client.py    — Multi-provider LLM client: Gemini → Cerebras → Groq (auto fallback)
  context.py       — Context compression for long runs
  subagent.py      — Isolated child agents for parallel deep-focus research

tools/             — 50 tools across 9 namespaces
  web/             — web_search, web_scrape, news_search, SEC EDGAR
  finance/         — financial_ratios, dcf_valuation, debt_risk_analysis, revenue_trend
  company/         — company_profile, leadership_research, market_position, acquisition_history
  risk/            — red_flag_scanner, risk_score_calculator, swot_generator, risk_impact_matrix
  sentiment/       — score_sentiment, detect_hedging_language, market_mood
  data/            — text_summarize, extract_entities, extract_keywords, text_clean
  output/          — compile_report, generate_outline, format_citations, critic_review
  research/        — fact_check, confidence_score, detect_contradictions, compare_financials
  file/            — file_read, file_write, file_list, file_exists

eval/
  judge.py         — LLM-as-judge eval harness (5 criteria, PASS ≥ 7.0/10 average)

tests/
  unit/            — 63 unit tests
  integration/     — 4 integration tests

models/            — Pydantic schemas for all tool inputs/outputs
observability/     — Structured logging (loguru)
app.py             — Streamlit UI with live phase badges and tool call feed
main.py            — CLI entry point
```

## Running the eval

```bash
python eval/judge.py outputs/apple_due_diligence.md
```

Scores a completed report on: completeness, data accuracy, risk coverage, structure,
actionability. Results saved to `outputs/eval_<filename>.md`.

## Key design decisions

- **Tool phase gating**: Only tools relevant to the current phase are sent to the LLM.
  Cuts token overhead ~70% and prevents the agent from running analysis before gathering data.
- **Multi-provider fallback**: Gemini rate-limits constantly on the free tier. Groq picks up
  silently. The agent never stops due to a single provider being unavailable.
- **Sub-agents**: Tasks like competitive landscape and litigation search get their own isolated
  agent with a 10-call budget, keeping the main context clean.
- **No hallucination policy**: If a number isn't in the tool results, the agent writes
  "not available" — it never invents figures.

## Test results

```
67 passed in ~22s
```
