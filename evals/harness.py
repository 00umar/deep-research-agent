"""
Evaluation harness — Day 3 implementation.

Will test the agent against a set of benchmark queries and score:
- Did the agent use at least 5 tools?
- Did it produce a report file?
- Did it cite sources?
- Did it use the subagent at least once?
- Did it complete within the tool call limit?
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class EvalCase:
    query: str
    min_tool_calls: int = 5
    expect_report_file: bool = True
    expect_sources: bool = True


@dataclass
class EvalResult:
    query: str
    passed: bool
    tool_calls_made: int
    report_saved: bool
    notes: List[str] = field(default_factory=list)


BENCHMARK_QUERIES = [
    EvalCase(query="What are the latest developments in quantum computing?", min_tool_calls=5),
    EvalCase(query="Compare electric vehicle battery technologies in 2025", min_tool_calls=8),
    EvalCase(query="Summarize the current state of large language model research", min_tool_calls=6),
]


def run_eval(query: str) -> EvalResult:
    """Run one evaluation case and return a scored result. Implemented Day 3."""
    raise NotImplementedError("Eval harness implemented on Day 3")
