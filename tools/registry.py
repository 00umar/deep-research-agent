from typing import Dict, Callable, Any
from google.genai import types
from loguru import logger


class ToolRegistry:
    """Central registry managing all agent tools across namespaces."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._declarations = []
        self._load_tools()
        logger.info(f"ToolRegistry: {self.tool_count} tools loaded")

    def _load_tools(self):
        from tools.web.search import web_search, web_search_declaration
        from tools.web.scrape import web_scrape, web_scrape_declaration
        from tools.file.reader import file_read, file_read_declaration
        from tools.file.writer import file_write, file_write_declaration
        from tools.data.summarize import text_summarize, text_summarize_declaration
        from tools.output.report import compile_report, compile_report_declaration
        from agent.subagent import spawn_research_subagent, spawn_research_subagent_declaration

        entries = [
            ("web_search",               web_search,               web_search_declaration),
            ("web_scrape",               web_scrape,               web_scrape_declaration),
            ("file_read",                file_read,                file_read_declaration),
            ("file_write",               file_write,               file_write_declaration),
            ("text_summarize",           text_summarize,           text_summarize_declaration),
            ("compile_report",           compile_report,           compile_report_declaration),
            ("spawn_research_subagent",  spawn_research_subagent,  spawn_research_subagent_declaration),
        ]

        for name, func, decl in entries:
            self._tools[name] = func
            self._declarations.append(decl)

    def get_gemini_tools(self):
        return [types.Tool(function_declarations=self._declarations)]

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
