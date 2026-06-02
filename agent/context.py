from typing import List, Dict, Any
from loguru import logger

COMPRESSION_THRESHOLD = 10
KEEP_RECENT = 5


class ContextManager:
    """
    Keeps the agent's memory from overflowing during long runs.

    Strategy: after every COMPRESSION_THRESHOLD tool calls, the oldest
    entries are collapsed into a single summary line. The agent always
    remembers what it set out to do and what it has done recently.
    """

    def __init__(self):
        self.tool_call_log: List[Dict[str, Any]] = []
        self.compression_count = 0

    def add_tool_call(self, tool_name: str, result: Any, call_number: int):
        self.tool_call_log.append({
            "call_number": call_number,
            "tool": tool_name,
            "result_preview": str(result)[:150]
        })

    def maybe_compress(self):
        if len(self.tool_call_log) >= COMPRESSION_THRESHOLD:
            self._compress()

    def _compress(self):
        if len(self.tool_call_log) <= KEEP_RECENT:
            return

        old = self.tool_call_log[:-KEEP_RECENT]
        recent = self.tool_call_log[-KEEP_RECENT:]

        usage: Dict[str, int] = {}
        for entry in old:
            usage[entry["tool"]] = usage.get(entry["tool"], 0) + 1

        summary = {
            "call_number": "compressed",
            "tool": "HISTORY_SUMMARY",
            "result_preview": f"{len(old)} earlier calls — " + ", ".join(f"{t}×{c}" for t, c in usage.items())
        }

        self.tool_call_log = [summary] + recent
        self.compression_count += 1
        logger.debug(f"Context compressed (pass {self.compression_count}): {len(old)} entries → 1 summary")

    def summary(self) -> str:
        lines = [f"Tool calls tracked: {len(self.tool_call_log)}"]
        for e in self.tool_call_log[-5:]:
            lines.append(f"  [{e['call_number']}] {e['tool']}")
        return "\n".join(lines)
