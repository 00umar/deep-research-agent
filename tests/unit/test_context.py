"""Tests for ContextManager message compression."""

from agent.context import ContextManager, COMPRESSION_THRESHOLD, KEEP_RECENT_TURNS


def _make_messages(n_tool_turns: int) -> list:
    """Build a fake messages list with n tool call turns."""
    msgs = [
        {"role": "system", "content": "You are a research agent."},
        {"role": "user", "content": "Research this topic."},
    ]
    for i in range(n_tool_turns):
        msgs.append({"role": "assistant", "content": f"Calling tool {i}"})
        msgs.append({"role": "tool", "tool_call_id": f"id_{i}", "content": f"Tool result {i}"})
        msgs.append({"role": "user", "content": "continue"})
    return msgs


def test_no_compression_below_threshold():
    ctx = ContextManager()
    msgs = _make_messages(3)  # 2 + 9 = 11 messages, below threshold
    result = ctx.maybe_compress(msgs)
    assert len(result) == len(msgs)
    assert ctx.compression_count == 0


def test_compression_above_threshold():
    ctx = ContextManager()
    # Add some tool call log entries so summary is meaningful
    for i in range(15):
        ctx.add_tool_call(f"tool_{i % 5}", {"result": i}, i + 1)

    msgs = _make_messages(10)  # 2 + 30 = 32 messages, above threshold
    result = ctx.maybe_compress(msgs)

    assert len(result) < len(msgs), "Compressed messages should be fewer"
    assert ctx.compression_count == 1


def test_system_message_always_kept():
    ctx = ContextManager()
    msgs = _make_messages(10)
    result = ctx.maybe_compress(msgs)
    system_msgs = [m for m in result if isinstance(m, dict) and m.get("role") == "system"]
    assert len(system_msgs) >= 1


def test_original_query_always_kept():
    ctx = ContextManager()
    msgs = _make_messages(10)
    result = ctx.maybe_compress(msgs)
    user_msgs = [m for m in result if isinstance(m, dict) and m.get("role") == "user"]
    first_user = next((m for m in result if isinstance(m, dict) and m.get("role") == "user"), None)
    assert first_user is not None
    assert "Research this topic" in first_user.get("content", "") or "RESEARCH PROGRESS SUMMARY" in first_user.get("content", "")


def test_compression_summary_mentions_tools():
    ctx = ContextManager()
    ctx.add_tool_call("web_search", {"results": []}, 1)
    ctx.add_tool_call("web_scrape", {"text": "..."}, 2)
    ctx.add_tool_call("text_summarize", {"summary": "..."}, 3)

    msgs = _make_messages(10)
    result = ctx.maybe_compress(msgs)

    summary_msgs = [m for m in result if "RESEARCH PROGRESS SUMMARY" in str(m.get("content", ""))]
    assert len(summary_msgs) == 1
    summary_text = summary_msgs[0]["content"]
    assert "web_search" in summary_text or "web_scrape" in summary_text
