"""
Subagent: an isolated child agent for focused deep-dives.

A subagent is NOT a renamed function. It gets:
  - Its own fresh Gemini chat (no access to parent conversation)
  - A scoped subset of tools (only what the task needs)
  - A structured result it returns to the parent

The parent agent calls spawn_research_subagent as a tool.
The subagent runs, does its work, and hands back a clean result.
"""

import os
import json
from google import genai
from google.genai import types
from loguru import logger
from typing import List

SUBAGENT_SYSTEM_PROMPT = """You are a focused research subagent. Investigate the assigned topic deeply.

Steps:
1. Search for information
2. Scrape the most relevant sources
3. Summarize your findings
4. Return a thorough written summary

Stay on task. Do not deviate from your assigned topic."""

SUBAGENT_TOOL_LIMIT = 10


class SubAgent:
    """Isolated child agent with scoped tools and a fresh context."""

    def __init__(self, task: str, allowed_tools: List[str] = None):
        self.task = task
        self.allowed_tools = allowed_tools or ["web_search", "web_scrape", "text_summarize"]

    def run(self) -> dict:
        logger.info(f"Subagent spawned | task: {self.task[:60]}...")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Import here to avoid circular imports at module load time
        from tools.registry import ToolRegistry
        registry = ToolRegistry()

        scoped_decls = [d for d in registry._declarations if d.name in self.allowed_tools]

        config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=scoped_decls)],
            system_instruction=SUBAGENT_SYSTEM_PROMPT
        )
        chat = client.chats.create(model="gemini-2.5-flash", config=config)
        response = chat.send_message(self.task)
        calls_made = 0

        while calls_made < SUBAGENT_TOOL_LIMIT:
            fn_calls = []
            try:
                for part in response.candidates[0].content.parts:
                    if part.function_call is not None and part.function_call.name:
                        fn_calls.append(part.function_call)
            except Exception:
                pass

            if not fn_calls:
                break

            parts = []
            for fc in fn_calls:
                calls_made += 1
                result = registry.execute(fc.name, dict(fc.args))
                parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": json.dumps(result, default=str)}
                    )
                )
            response = chat.send_message(parts)

        logger.info(f"Subagent done | {calls_made} tool calls")
        try:
            result_text = response.text
        except Exception:
            result_text = "Subagent completed but returned no final text."

        return {
            "task": self.task,
            "result": result_text,
            "tool_calls_made": calls_made,
            "tools_available": self.allowed_tools
        }


def spawn_research_subagent(topic: str) -> dict:
    """Tool wrapper: spawn an isolated subagent to deeply research a specific topic."""
    return SubAgent(
        task=f"Deeply research this topic and provide comprehensive findings: {topic}",
        allowed_tools=["web_search", "web_scrape", "text_summarize"]
    ).run()


spawn_research_subagent_declaration = types.FunctionDeclaration(
    name="spawn_research_subagent",
    description="Spawn an isolated subagent to deeply research a specific sub-topic. The subagent has its own context and scoped tools. Use this for focused deep-dives on one aspect of your research.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "topic": types.Schema(
                type=types.Type.STRING,
                description="The specific topic or question for the subagent to investigate"
            )
        },
        required=["topic"]
    )
)
