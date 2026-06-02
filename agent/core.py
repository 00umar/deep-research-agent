import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from loguru import logger
from observability.logger import setup_logger
from agent.context import ContextManager
from tools.registry import ToolRegistry

load_dotenv()
setup_logger()

MAX_TOOL_CALLS = 50

from datetime import date as _date

SYSTEM_PROMPT = f"""You are an autonomous deep research agent. Today's date is {_date.today().isoformat()}.
Your job is to thoroughly research any topic and produce a comprehensive report.

Research process:
1. Start with broad web searches to understand the topic
2. Scrape the most relevant pages for detail
3. For complex sub-topics, use spawn_research_subagent for a focused deep-dive
4. Summarize scraped content with text_summarize before storing
5. Save notes to files as you go with file_write
6. At the end, compile everything into a final report with compile_report

Always use your tools — do not answer from memory alone. Always cite your sources."""


class ResearchAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing. Add it to your .env file.")

        self.client = genai.Client(api_key=api_key)
        self.registry = ToolRegistry()
        self.context = ContextManager()
        self.tool_call_count = 0

        config = types.GenerateContentConfig(
            tools=self.registry.get_gemini_tools(),
            system_instruction=SYSTEM_PROMPT
        )
        self.chat = self.client.chats.create(model="gemini-2.5-flash", config=config)
        logger.info(f"ResearchAgent ready | {self.registry.tool_count} tools")

    def run(self, query: str) -> str:
        logger.info(f"Query: {query}")
        response = self.chat.send_message(query)

        while self.tool_call_count < MAX_TOOL_CALLS:
            fn_calls = self._extract_fn_calls(response)

            if not fn_calls:
                logger.info(f"Done. Total tool calls: {self.tool_call_count}")
                try:
                    return response.text
                except Exception:
                    return "Research complete. Check the outputs/ folder for your report."

            tool_parts = []
            for fc in fn_calls:
                self.tool_call_count += 1
                logger.info(f"[{self.tool_call_count}] {fc.name}")
                result = self.registry.execute(fc.name, dict(fc.args))
                self.context.add_tool_call(fc.name, result, self.tool_call_count)
                tool_parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": json.dumps(result, default=str)}
                    )
                )

            self.context.maybe_compress()
            response = self.chat.send_message(tool_parts)

        logger.warning(f"Reached tool call limit ({MAX_TOOL_CALLS}).")
        try:
            return response.text
        except Exception:
            return "Tool call limit reached. Check outputs/ for partial results."

    def _extract_fn_calls(self, response):
        calls = []
        try:
            for part in response.candidates[0].content.parts:
                if part.function_call is not None and part.function_call.name:
                    calls.append(part.function_call)
        except Exception:
            pass
        return calls
