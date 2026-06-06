# MEMO

## What I Built

An autonomous corporate due diligence agent that takes a plain-English research question
and produces a structured, cited report — without any human guidance on which tools to use
or in what order.

**Core architecture:**
- **5-phase workflow** (plan → gather → process → analyze → output): Each phase exposes only
  the tools relevant to that stage. The agent can't run SWOT analysis before it has gathered
  data — the phase gates enforce the sequence a real analyst would follow.
- **Multi-provider LLM client** (`agent/llm_client.py`): Priority order is Gemini →
  Cerebras → Groq (fast) → Groq (quality). Automatic fallback on rate limits, 6-second
  minimum gap between calls, 65-second reset wait when all providers are exhausted. In
  practice, Gemini rate-limits on almost every call on the free tier; Groq handles the
  fallback silently. The agent keeps running regardless.
- **50 tools across 9 namespaces**: web (search, scrape, news, SEC EDGAR), file (read,
  write, list, exists), finance (ratios, DCF, debt risk, revenue trend), company (profile,
  leadership, market position, acquisition history, earnings), risk (red flag scanner,
  risk score, SWOT, impact matrix, contradiction detection), sentiment (scoring, hedging
  language detection), data (summarize, clean, keywords, entities), output (compile report,
  outline, citations, timeline, critic review), research (fact check, confidence score,
  compare financials).
- **Sub-agents** (`agent/subagent.py`): 7 tools spawn isolated child agents (each capped
  at 10 tool calls) to handle deep-focus tasks in parallel — competitive landscape,
  litigation search, company profile, leadership research, market position, market mood,
  fact checking. This keeps the main agent context clean.
- **Context compression** (`agent/context.py`): When the conversation exceeds 20 messages,
  older turns are collapsed into a summary. The main agent ran 32 tool calls on Tesla with
  23 compression passes — context stayed manageable throughout.
- **Token efficiency**: Sending all 50 tool definitions every call would be wasteful. The
  TOOL_PHASES dict restricts visible tools per phase, cutting the tool payload by ~70%.
- **LLM-as-judge eval harness** (`eval/judge.py`): Scores completed reports on 5 criteria
  (completeness, data accuracy, risk coverage, structure, actionability), 0–10 each. PASS
  threshold is 7.0 average. Apple Inc. report scored 82% (PASS). Tesla scored 66% (BORDERLINE
  — missing live financial figures; see "What More Time Would Have Addressed").
- **Streamlit UI** (`app.py`): Live phase badges, per-tool call feed, real-time progress bar,
  rendered report with download button.
- **67 tests**: 63 unit + 4 integration, all passing.

## What I Cut

- `link_extractor`, `url_check`, `page_metadata` were removed from the gather phase. They
  added scraping overhead but contributed almost no signal to a due diligence report. Cutting
  them freed gather budget for SEC filings and financial data.
- `market_mood` is registered as a tool but intentionally left out of TOOL_PHASES. It can
  only be called internally by other tools (never directly by the agent). Without data to
  analyze first, an agent calling sentiment tools early produces noise.
- `evals/harness.py` was a Day 1 stub with hardcoded benchmark queries. It was superseded by
  the proper LLM-as-judge harness in `eval/judge.py` and left in place as a historical
  artifact. It is not called anywhere.

## What More Time Would Have Addressed

- **Real financial data extraction from SEC filings**: The agent retrieves filing metadata from
  EDGAR but does not parse XBRL financial tables. For Tesla, revenue, net income, and total
  debt all came back "not available." A proper XBRL parser (or a targeted scrape of the
  filing viewer) would fix this. Apple worked better because its investor page had readable
  financial text.
- **Longer gather phase**: `PHASE_MAX_CALLS` for gather is 6. For companies with complex
  corporate structures, 6 gather calls isn't always enough to cover subsidiaries, recent
  earnings, and filings. Raising the limit or making it configurable per query would help.
- **Context loss after many compressions**: After 20+ compression passes on a long run,
  some early tool results get folded into summaries and the specific numbers are dropped.
  A retrieval layer (e.g. a local vector store of all tool outputs) would solve this properly.

## One Design Decision I Would Defend

**Tool phase gating** (the `TOOL_PHASES` dict in `agent/core.py`).

The simplest design would send all 50 tools every call and let the LLM decide. I didn't do
that. Instead, each phase exposes only the tools that make sense at that stage. The plan phase
gets one tool. The gather phase gets research tools. The analyze phase gets pure-Python
calculators only — no API calls, no new information gathering.

Why defend this? Three reasons:

1. **Token cost**: 50 tool definitions × ~200 tokens each = ~10,000 tokens of overhead per
   call. With 32 tool calls, that's 320,000 tokens wasted on tools the agent couldn't use
   anyway. Phase gating cuts this by ~70%.

2. **Agent discipline**: Without phase gating, LLMs have a tendency to jump to conclusions —
   running SWOT or DCF before gathering enough data, then producing analysis based on thin
   evidence. Phase gating enforces the same sequence a real analyst would follow: research
   first, conclude later.

3. **Debuggability**: When something goes wrong, I know which phase it was in and which tools
   were available. A flat tool list makes that harder to trace.

The cost is rigidity — if the agent genuinely needs to re-gather in the middle of analysis,
it can't. In practice, the 5-phase structure matched real due diligence workflows closely
enough that this never caused a problem in testing.
