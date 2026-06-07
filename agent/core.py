import os
import json
from datetime import date as _date
from dotenv import load_dotenv
from loguru import logger
from observability.logger import setup_logger
from agent.context import ContextManager
from agent.llm_client import LLMClient
from tools.registry import ToolRegistry

load_dotenv()
setup_logger()

MAX_TOOL_CALLS = 50

# Tools grouped by research phase — only the relevant group is sent per call.
# This cuts tokens per request by ~70% compared to sending all 50 every time.
TOOL_PHASES = {
    "plan":    ["generate_outline"],
    # link_extractor / url_check / page_metadata removed — low signal for due diligence, waste gather budget
    "gather":  ["web_search", "web_scrape", "news_search",
                "sec_search", "fetch_10k_summary", "company_profile", "leadership_research"],
    "process": ["text_summarize", "extract_keywords", "extract_entities", "file_read",
                "extract_financial_data", "score_sentiment", "detect_hedging_language",
                "compile_report", "file_write"],   # compile_report → file_write must happen here
    # analyze = pure Python only (zero extra API calls each)
    "analyze": ["financial_ratios", "revenue_trend", "debt_risk_analysis",
                "red_flag_scanner", "risk_score_calculator",
                "detect_contradictions", "confidence_score", "fact_check"],
    "output":  ["swot_generator", "risk_impact_matrix", "compare_financials", "dcf_valuation",
                "comparison_matrix", "compile_report", "format_citations", "critic_review",
                "file_write", "file_list", "market_position", "competitive_landscape",
                "acquisition_history", "earnings_summary", "litigation_search"],
}

# Max tool calls allowed per phase before forcing advancement.
PHASE_MAX_CALLS = {
    "plan":    1,
    "gather":  6,
    "process": 8,   # increased — must fit extract + compile_report + file_write
    "analyze": 6,
    "output":  6,
}

PHASE_ORDER = ["plan", "gather", "process", "analyze", "output"]

SYSTEM_PROMPT = f"""You are an autonomous corporate due diligence agent. Today's date is {_date.today().isoformat()}.
Your job is to investigate companies and produce structured due diligence reports
for investment, acquisition, or partnership decisions.

RULE: Only call a tool when you need what it produces. Calling tools without real input data
wastes quota and produces noise. Quality over quantity.

Core workflow (minimum required):
1. generate_outline — identify what dimensions to investigate
2. Gather real data — sec_search and/or web_search for actual facts and figures
3. compile_report — synthesize all findings into a structured markdown report
4. file_write — save to outputs/ with a descriptive filename

Use additional tools when the situation calls for them:
- web_scrape: when a URL has detailed content worth reading in full
- extract_financial_data: when scraped text contains revenue/profit/debt figures
- financial_ratios + debt_risk_analysis: only when you have actual numbers
- red_flag_scanner + risk_score_calculator: when you have substantial text to scan
- news_search: when recent events could affect the investment decision
- swot_generator + risk_impact_matrix: when you have enough data for meaningful analysis

Always cite sources. Stop when the report is saved."""


def _clean_msg(msg) -> dict:
    """Strip provider-specific fields (e.g. Groq's 'reasoning') before storing in message history."""
    cleaned = {"role": msg.role, "content": msg.content}
    if msg.tool_calls:
        cleaned["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in msg.tool_calls
        ]
    return cleaned


class ResearchAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.registry = ToolRegistry()
        self.context = ContextManager()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tool_call_count = 0
        self._phase_index = 0
        self._phase_call_counts: dict = {p: 0 for p in PHASE_ORDER}
        self.on_event = None  # optional callback(event_dict) for UI progress updates
        logger.info(
            f"ResearchAgent ready | {self.registry.tool_count} tools | "
            f"providers: {[p['name'] for p in self.llm._available]} | "
            f"active: {self.llm.active_provider}"
        )

    @property
    def _current_phase(self) -> str:
        return PHASE_ORDER[self._phase_index]

    def _tools_for_phase(self) -> list:
        names = TOOL_PHASES[self._current_phase]
        return [t for t in self.registry.get_tools() if t["function"]["name"] in names]

    def _advance_phase(self):
        if self._phase_index < len(PHASE_ORDER) - 1:
            self._phase_index += 1
            logger.info(f"Phase advanced -> {self._current_phase}")
            if self.on_event:
                self.on_event({"type": "phase_change", "phase": self._current_phase})

    def _should_advance(self, tool_name: str) -> bool:
        """Advance phase when a tool from the next phase is needed."""
        current_tools = TOOL_PHASES[self._current_phase]
        if tool_name not in current_tools:
            for i, phase in enumerate(PHASE_ORDER):
                if tool_name in TOOL_PHASES[phase] and i > self._phase_index:
                    return True
        return False

    def run(self, query: str) -> str:
        logger.info(f"Query: {query[:80]}...")
        self.messages.append({"role": "user", "content": query})
        if self.on_event:
            self.on_event({"type": "phase_change", "phase": self._current_phase})
        response, _ = self.llm.complete(self.messages, self._tools_for_phase())

        while self.tool_call_count < MAX_TOOL_CALLS:
            msg = response.choices[0].message
            tool_calls = msg.tool_calls or []

            if not tool_calls:
                content = msg.content or ""

                # Model wrote tool call as text — correct and retry
                if "<function(" in content or "<function=" in content:
                    logger.warning("Model output tool call as text — injecting format correction...")
                    self.messages.append({"role": "assistant", "content": content})
                    self.messages.append({
                        "role": "user",
                        "content": (
                            "You wrote a tool call as plain text. That does not execute anything. "
                            "Use the structured tool_call format and call the same tool now."
                        ),
                    })
                    self.messages = self.context.maybe_compress(self.messages)
                    response, _ = self.llm.complete(self.messages, self._tools_for_phase())
                    continue

                # Model may need more tools — try advancing phase before stopping
                if self._phase_index < len(PHASE_ORDER) - 1:
                    self._advance_phase()
                    self.messages.append({"role": "assistant", "content": content or ""})
                    self.messages.append({
                        "role": "user",
                        "content": (
                            f"Good progress. Now move to the next research phase. "
                            f"Available tools for this phase: {', '.join(TOOL_PHASES[self._current_phase])}. "
                            f"Continue the task — do not stop until file_write has been called to save the report."
                        ),
                    })
                    self.messages = self.context.maybe_compress(self.messages)
                    response, _ = self.llm.complete(self.messages, self._tools_for_phase())
                    continue

                logger.info(f"Done. Total tool calls: {self.tool_call_count}")
                return content or "Research complete. Check the outputs/ folder for your report."

            self.messages.append(_clean_msg(msg))

            _stop_after_batch = False
            for tc in tool_calls:
                self.tool_call_count += 1
                name = tc.function.name
                logger.info(f"[{self.tool_call_count}] {name} (phase: {self._current_phase})")

                # Auto-advance phase if needed
                if self._should_advance(name):
                    self._advance_phase()

                args = json.loads(tc.function.arguments)
                result = self.registry.execute(name, args)
                self.context.add_tool_call(name, result, self.tool_call_count)
                if self.on_event:
                    self.on_event({
                        "type": "tool_call",
                        "number": self.tool_call_count,
                        "name": name,
                        "phase": self._current_phase,
                        "result_preview": str(result)[:150].replace("\n", " "),
                    })
                content_str = json.dumps(result, default=str)
                if len(content_str) > 2500:
                    content_str = content_str[:2500] + f"... [truncated — full result stored in context log #{self.tool_call_count}]"
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": content_str,
                })

                # Track per-phase usage and advance when limit is hit
                self._phase_call_counts[self._current_phase] += 1
                phase_limit = PHASE_MAX_CALLS.get(self._current_phase, 8)
                if self._phase_call_counts[self._current_phase] >= phase_limit:
                    if self._phase_index < len(PHASE_ORDER) - 1:
                        self._advance_phase()
                    else:
                        # Output phase limit reached — stop cleanly
                        logger.info("Output phase limit reached — stopping.")
                        _stop_after_batch = True
                        break

            if _stop_after_batch:
                break

            self.messages = self.context.maybe_compress(self.messages)
            response, provider = self.llm.complete(self.messages, self._tools_for_phase())
            if provider != self.llm.active_provider:
                logger.info(f"Provider switched to: {provider}")

        logger.warning(f"Reached tool call limit ({MAX_TOOL_CALLS}).")
        return response.choices[0].message.content or "Tool call limit reached. Check outputs/ for partial results."
