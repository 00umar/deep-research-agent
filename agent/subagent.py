"""
Subagent: an isolated child agent for focused deep-dives.

A subagent is NOT a renamed function. It gets:
  - Its own fresh chat (no access to parent conversation)
  - A scoped subset of tools (only what the task needs)
  - A structured result it returns to the parent

The parent agent calls spawn_research_subagent as a tool.
The subagent runs, does its work, and hands back a clean result.
"""

import json
from loguru import logger
from typing import List
from agent.llm_client import LLMClient

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
        llm = LLMClient()

        # Import here to avoid circular imports at module load time
        from tools.registry import ToolRegistry
        registry = ToolRegistry()

        scoped_tools = [
            t for t in registry.get_tools()
            if t["function"]["name"] in self.allowed_tools
        ]

        messages = [
            {"role": "system", "content": SUBAGENT_SYSTEM_PROMPT},
            {"role": "user", "content": self.task}
        ]

        def send():
            response, provider = llm.complete(messages, scoped_tools)
            return response

        response = send()
        calls_made = 0

        while calls_made < SUBAGENT_TOOL_LIMIT:
            msg = response.choices[0].message
            tool_calls = msg.tool_calls or []

            if not tool_calls:
                content = msg.content or ""
                if "<function(" in content or "<function=" in content:
                    logger.warning("Subagent: text tool call detected — injecting correction...")
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user",
                        "content": (
                            "You wrote a tool call as plain text. That does not execute anything. "
                            "Use the structured tool_call format and call the same tool now."
                        )
                    })
                    response = send()
                    continue
                break

            cleaned = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                cleaned["tool_calls"] = [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ]
            messages.append(cleaned)

            for tc in tool_calls:
                calls_made += 1
                args = json.loads(tc.function.arguments)
                result = registry.execute(tc.function.name, args)
                content_str = json.dumps(result, default=str)
                if len(content_str) > 2500:
                    content_str = content_str[:2500] + "... [truncated]"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": content_str
                })

            response = send()

        logger.info(f"Subagent done | {calls_made} tool calls")
        result_text = response.choices[0].message.content or "Subagent completed but returned no final text."

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


spawn_research_subagent_declaration = {
    "type": "function",
    "function": {
        "name": "spawn_research_subagent",
        "description": "Spawn an isolated subagent to deeply research a specific sub-topic. The subagent has its own context and scoped tools. Use this for focused deep-dives on one aspect of your research.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The specific topic or question for the subagent to investigate"
                }
            },
            "required": ["topic"]
        }
    }
}
