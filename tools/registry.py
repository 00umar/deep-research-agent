from typing import Dict, Callable, Any
from loguru import logger


class ToolRegistry:
    """Central registry managing all agent tools across namespaces."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._declarations = []
        self._load_tools()
        logger.info(f"ToolRegistry: {self.tool_count} tools loaded")

    def _load_tools(self):
        # Web
        from tools.web.search import web_search, web_search_declaration
        from tools.web.scrape import web_scrape, web_scrape_declaration
        from tools.web.news import news_search, news_search_declaration
        from tools.web.links import link_extractor, link_extractor_declaration
        from tools.web.metadata import page_metadata, page_metadata_declaration
        from tools.web.urlcheck import url_check, url_check_declaration
        # File
        from tools.file.reader import file_read, file_read_declaration
        from tools.file.writer import file_write, file_write_declaration
        from tools.file.lister import file_list, file_list_declaration
        from tools.file.exists import file_exists, file_exists_declaration
        # Data
        from tools.data.summarize import text_summarize, text_summarize_declaration
        from tools.data.clean import text_clean, text_clean_declaration
        from tools.data.keywords import extract_keywords, extract_keywords_declaration
        from tools.data.entities import extract_entities, extract_entities_declaration
        # Output
        from tools.output.report import compile_report, compile_report_declaration
        from tools.output.timeline import build_timeline, build_timeline_declaration
        from tools.output.compare import comparison_matrix, comparison_matrix_declaration
        from tools.output.citations import format_citations, format_citations_declaration
        from tools.output.outline import generate_outline, generate_outline_declaration
        # Research capabilities
        from tools.research.perspectives import multi_perspective_research, multi_perspective_research_declaration
        from tools.research.factcheck import fact_check, fact_check_declaration
        from tools.research.contradict import detect_contradictions, detect_contradictions_declaration
        from tools.research.confidence import confidence_score, confidence_score_declaration
        from tools.research.critic import critic_review, critic_review_declaration
        # Agent
        from agent.subagent import spawn_research_subagent, spawn_research_subagent_declaration
        # Finance
        from tools.finance.sec_filings import (sec_search, sec_search_declaration,
                                                fetch_10k_summary, fetch_10k_summary_declaration)
        from tools.finance.ratios import (financial_ratios, financial_ratios_declaration,
                                          dcf_valuation, dcf_valuation_declaration,
                                          revenue_trend, revenue_trend_declaration,
                                          debt_risk_analysis, debt_risk_analysis_declaration)
        from tools.finance.compare_tools import (compare_financials, compare_financials_declaration,
                                                  extract_financial_data, extract_financial_data_declaration)
        from tools.finance.earnings import earnings_summary, earnings_summary_declaration
        # Sentiment
        from tools.sentiment.analyzer import (score_sentiment, score_sentiment_declaration,
                                               aggregate_sentiment, aggregate_sentiment_declaration,
                                               detect_hedging_language, detect_hedging_language_declaration,
                                               market_mood, market_mood_declaration)
        # Risk
        from tools.risk.scanner import (red_flag_scanner, red_flag_scanner_declaration,
                                         risk_score_calculator, risk_score_calculator_declaration,
                                         litigation_search, litigation_search_declaration)
        from tools.risk.analysis import (swot_generator, swot_generator_declaration,
                                          risk_impact_matrix, risk_impact_matrix_declaration,
                                          competitive_landscape, competitive_landscape_declaration)
        # Company
        from tools.company.profile import (company_profile, company_profile_declaration,
                                            leadership_research, leadership_research_declaration,
                                            market_position, market_position_declaration)
        from tools.company.history import (acquisition_history, acquisition_history_declaration,
                                            supply_chain_analysis, supply_chain_analysis_declaration,
                                            patent_search, patent_search_declaration)

        entries = [
            # ── Original 25 ────────────────────────────────────────────────────
            ("web_search",                 web_search,                 web_search_declaration),
            ("web_scrape",                 web_scrape,                 web_scrape_declaration),
            ("news_search",                news_search,                news_search_declaration),
            ("link_extractor",             link_extractor,             link_extractor_declaration),
            ("page_metadata",              page_metadata,              page_metadata_declaration),
            ("url_check",                  url_check,                  url_check_declaration),
            ("file_read",                  file_read,                  file_read_declaration),
            ("file_write",                 file_write,                 file_write_declaration),
            ("file_list",                  file_list,                  file_list_declaration),
            ("file_exists",                file_exists,                file_exists_declaration),
            ("text_summarize",             text_summarize,             text_summarize_declaration),
            ("text_clean",                 text_clean,                 text_clean_declaration),
            ("extract_keywords",           extract_keywords,           extract_keywords_declaration),
            ("extract_entities",           extract_entities,           extract_entities_declaration),
            ("compile_report",             compile_report,             compile_report_declaration),
            ("build_timeline",             build_timeline,             build_timeline_declaration),
            ("comparison_matrix",          comparison_matrix,          comparison_matrix_declaration),
            ("format_citations",           format_citations,           format_citations_declaration),
            ("generate_outline",           generate_outline,           generate_outline_declaration),
            ("multi_perspective_research", multi_perspective_research, multi_perspective_research_declaration),
            ("fact_check",                 fact_check,                 fact_check_declaration),
            ("detect_contradictions",      detect_contradictions,      detect_contradictions_declaration),
            ("confidence_score",           confidence_score,           confidence_score_declaration),
            ("critic_review",              critic_review,              critic_review_declaration),
            ("spawn_research_subagent",    spawn_research_subagent,    spawn_research_subagent_declaration),
            # ── Finance namespace (9) ──────────────────────────────────────────
            ("sec_search",                 sec_search,                 sec_search_declaration),
            ("fetch_10k_summary",          fetch_10k_summary,          fetch_10k_summary_declaration),
            ("financial_ratios",           financial_ratios,           financial_ratios_declaration),
            ("dcf_valuation",              dcf_valuation,              dcf_valuation_declaration),
            ("revenue_trend",              revenue_trend,              revenue_trend_declaration),
            ("debt_risk_analysis",         debt_risk_analysis,         debt_risk_analysis_declaration),
            ("compare_financials",         compare_financials,         compare_financials_declaration),
            ("extract_financial_data",     extract_financial_data,     extract_financial_data_declaration),
            ("earnings_summary",           earnings_summary,           earnings_summary_declaration),
            # ── Sentiment namespace (4) ────────────────────────────────────────
            ("score_sentiment",            score_sentiment,            score_sentiment_declaration),
            ("aggregate_sentiment",        aggregate_sentiment,        aggregate_sentiment_declaration),
            ("detect_hedging_language",    detect_hedging_language,    detect_hedging_language_declaration),
            ("market_mood",                market_mood,                market_mood_declaration),
            # ── Risk namespace (6) ─────────────────────────────────────────────
            ("red_flag_scanner",           red_flag_scanner,           red_flag_scanner_declaration),
            ("risk_score_calculator",      risk_score_calculator,      risk_score_calculator_declaration),
            ("litigation_search",          litigation_search,          litigation_search_declaration),
            ("swot_generator",             swot_generator,             swot_generator_declaration),
            ("risk_impact_matrix",         risk_impact_matrix,         risk_impact_matrix_declaration),
            ("competitive_landscape",      competitive_landscape,      competitive_landscape_declaration),
            # ── Company namespace (6) ──────────────────────────────────────────
            ("company_profile",            company_profile,            company_profile_declaration),
            ("leadership_research",        leadership_research,        leadership_research_declaration),
            ("market_position",            market_position,            market_position_declaration),
            ("acquisition_history",        acquisition_history,        acquisition_history_declaration),
            ("supply_chain_analysis",      supply_chain_analysis,      supply_chain_analysis_declaration),
            ("patent_search",              patent_search,              patent_search_declaration),
        ]

        for name, func, decl in entries:
            self._tools[name] = func
            self._declarations.append(decl)

    def get_tools(self):
        return self._declarations

    def execute(self, name: str, args: Dict[str, Any]) -> Any:
        if name not in self._tools:
            logger.warning(f"Unknown tool requested: {name}")
            return {"error": "ToolNotFound", "message": f"Tool '{name}' not registered"}
        try:
            logger.debug(f"Executing {name} | args: {list(args.keys())}")
            return self._tools[name](**args)
        except TypeError as e:
            return {"error": "InvalidArgs", "message": str(e)}
        except Exception as e:
            logger.error(f"Tool {name} raised: {e}")
            return {"error": type(e).__name__, "message": str(e)}

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    @property
    def tool_names(self):
        return list(self._tools.keys())
