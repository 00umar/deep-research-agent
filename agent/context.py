"""
Context manager for long-horizon agent runs.

Problem: each tool call adds 2-3 messages to the conversation history.
After 20+ tool calls, the history is thousands of tokens long. The model
starts losing its original plan in the noise and quality degrades.

Strategy:
- Track every tool call in a structured log
- When the messages list exceeds COMPRESSION_THRESHOLD, collapse the oldest
  messages into a single plain-text summary injected back into the conversation
- Always keep: system prompt, original user query, last KEEP_RECENT_TURNS turns
- The summary tells the model what it has already done so it can continue coherently
"""

from typing import List, Dict, Any
from loguru import logger

COMPRESSION_THRESHOLD = 20   # compress after this many messages
KEEP_RECENT_TURNS = 6        # always keep the last N tool call turns (each turn = ~3 messages)


class ContextManager:

    def __init__(self):
        self.tool_call_log: List[Dict[str, Any]] = []
        self.compression_count = 0

    def add_tool_call(self, tool_name: str, result: Any, call_number: int):
        self.tool_call_log.append({
            "call_number": call_number,
            "tool": tool_name,
            "result_preview": str(result)[:200],
        })

    def maybe_compress(self, messages: list) -> list:
        """
        If messages list is too long, collapse the middle into a summary.
        Returns the (possibly compressed) messages list.
        """
        if len(messages) <= COMPRESSION_THRESHOLD:
            return messages

        # Split: system messages stay, first user message stays, rest is compressible
        system_msgs = [m for m in messages if isinstance(m, dict) and m.get("role") == "system"]
        non_system = [m for m in messages if not (isinstance(m, dict) and m.get("role") == "system")]

        # Keep original query (first user message) + recent turns
        if not non_system:
            return messages

        first_user = [non_system[0]] if non_system else []
        rest = non_system[1:]

        keep_count = KEEP_RECENT_TURNS * 3  # 3 messages per turn: assistant + tool_result + next
        if len(rest) <= keep_count:
            return messages  # not enough to compress yet

        to_compress = rest[:-keep_count]
        recent = rest[-keep_count:]

        summary = self._build_summary(to_compress)
        summary_msg = {
            "role": "user",
            "content": (
                f"[RESEARCH PROGRESS SUMMARY — {len(to_compress)} earlier messages compressed]\n\n"
                f"{summary}\n\n"
                "Continue the research plan. Pick up exactly where you left off."
            ),
        }

        compressed = system_msgs + first_user + [summary_msg] + recent
        self.compression_count += 1
        logger.info(
            f"Context compressed (pass {self.compression_count}): "
            f"{len(messages)} messages -> {len(compressed)} "
            f"({len(to_compress)} collapsed into 1 summary)"
        )
        return compressed

    def _build_summary(self, messages: list) -> str:
        """Build a human-readable summary of what happened in compressed messages."""
        # Use the tool_call_log which is already structured
        if not self.tool_call_log:
            return "Research has been in progress. Multiple tools have been called."

        recent_log_count = len(self.tool_call_log) - KEEP_RECENT_TURNS
        if recent_log_count <= 0:
            log_entries = self.tool_call_log
        else:
            log_entries = self.tool_call_log[:recent_log_count]

        tool_counts: Dict[str, int] = {}
        for entry in log_entries:
            tool_counts[entry["tool"]] = tool_counts.get(entry["tool"], 0) + 1

        lines = ["Tools already executed (do not repeat unless necessary):"]
        for tool, count in tool_counts.items():
            lines.append(f"  - {tool} × {count}")

        if log_entries:
            last = log_entries[-1]
            lines.append(f"\nLast completed action: [{last['call_number']}] {last['tool']}")
            lines.append(f"Result preview: {last['result_preview'][:300]}")

        return "\n".join(lines)

    @property
    def tools_used(self) -> List[str]:
        return [e["tool"] for e in self.tool_call_log]

    @property
    def call_count(self) -> int:
        return len(self.tool_call_log)

    def summary(self) -> str:
        lines = [f"Tool calls made: {self.call_count}"]
        for e in self.tool_call_log[-5:]:
            lines.append(f"  [{e['call_number']}] {e['tool']}")
        return "\n".join(lines)
