import os
import glob
import threading
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Due Diligence Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimal styling ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.phase-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.phase-plan    { background: #1E3A5F; color: #7EB8F7; }
.phase-gather  { background: #3D2B00; color: #FFB347; }
.phase-process { background: #2D1B4E; color: #C39BD3; }
.phase-analyze { background: #4A1A1A; color: #F1948A; }
.phase-output  { background: #1A3A2A; color: #82E0AA; }
.tool-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 6px;
    padding: 6px 8px;
    border-radius: 6px;
    background: #1E1E1E;
}
.tool-num { color: #888; font-size: 12px; min-width: 26px; }
.tool-name { font-family: monospace; font-size: 13px; color: #E8E8E8; }
.tool-preview { font-size: 11px; color: #999; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Shared run state (plain Python object — safe to write from background thread) ──
class AgentRun:
    """Holds live state for one agent run. Thread writes to this; UI reads from it."""
    def __init__(self):
        self.events: list = []
        self.running: bool = True
        self.report: str | None = None
        self.error: str | None = None


# ── Session state init ─────────────────────────────────────────────────────────
if "current_run" not in st.session_state:
    st.session_state.current_run = None


# ── Task builder (same as main.py) ─────────────────────────────────────────────
def build_task(query: str) -> str:
    return f"""Due diligence task: {query}

Your goal: Produce a complete, well-sourced due diligence report saved to the outputs/ folder.

REQUIRED steps — execute in this order:
1. generate_outline — identify the due diligence dimensions to investigate
2. sec_search — find real SEC filings for the company
3. web_search — 1-2 targeted searches for financial data and recent news
4. extract_financial_data — pull revenue, profit, debt from any scraped content
5. compile_report — synthesize ALL findings into a full structured markdown report
6. file_write — save the compiled report to outputs/ (e.g. outputs/apple_due_diligence.md)
7. Reply with a 3-5 sentence summary + exact filename saved

IMPORTANT rules:
- compile_report MUST be called before file_write — do not write a file until you have compiled
- Only include facts from tool results — do not invent company names, figures, or events
- If a number is not in your tool results, say "not available" rather than guessing

OPTIONAL — use only when data supports it:
- web_scrape: if a source has detailed content worth reading in full
- news_search: if recent events are relevant to the decision
- financial_ratios + debt_risk_analysis: only with actual revenue/debt numbers
- red_flag_scanner: if you have substantial text that might hide warnings
- swot_generator + risk_impact_matrix: when you have enough data for meaningful analysis

Stop when the report is saved."""


# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Due Diligence Agent")
st.caption("Autonomous corporate due diligence · Gemini · Groq · Cerebras · 50 tools · 9 namespaces")

st.divider()

# ── Query input ────────────────────────────────────────────────────────────────
run: AgentRun | None = st.session_state.current_run
is_running = run is not None and run.running

col_q, col_btn = st.columns([5, 1])
with col_q:
    query = st.text_input(
        "Research question",
        placeholder="e.g. Conduct due diligence on Apple Inc. for a hypothetical acquisition",
        label_visibility="collapsed",
        disabled=is_running,
    )
with col_btn:
    start_clicked = st.button(
        "Research →",
        disabled=is_running or not query,
        type="primary",
        use_container_width=True,
    )

# ── Start agent ────────────────────────────────────────────────────────────────
if start_clicked and query and not is_running:
    new_run = AgentRun()
    st.session_state.current_run = new_run

    def run_agent_thread(q: str, agent_run: AgentRun):
        try:
            from agent.core import ResearchAgent
            os.makedirs("outputs", exist_ok=True)
            agent = ResearchAgent()
            # Thread writes only to agent_run (plain Python object) — no st.session_state calls
            agent.on_event = lambda e: agent_run.events.append(e)
            result = agent.run(build_task(q))
            agent_run.report = result
        except Exception as exc:
            agent_run.error = str(exc)
        finally:
            agent_run.running = False

    t = threading.Thread(target=run_agent_thread, args=(query, new_run), daemon=True)
    t.start()
    st.rerun()

st.divider()

# ── Read current run state ─────────────────────────────────────────────────────
run: AgentRun | None = st.session_state.current_run
is_running = run is not None and run.running
events = run.events if run else []
report_text = run.report if run else None
error = run.error if run else None

# ── Main layout ────────────────────────────────────────────────────────────────
PHASE_ORDER = ["plan", "gather", "process", "analyze", "output"]
PHASE_LABELS = {
    "plan":    ("🗺️",  "plan"),
    "gather":  ("🌐", "gather"),
    "process": ("⚙️",  "process"),
    "analyze": ("🔍", "analyze"),
    "output":  ("📄", "output"),
}

col_left, col_right = st.columns([2, 3], gap="large")

# ── Left: live activity ────────────────────────────────────────────────────────
with col_left:
    if is_running:
        st.markdown("**Live Activity** &nbsp; 🟢 Running...")
    elif events:
        st.markdown("**Live Activity** &nbsp; ✅ Complete")
    else:
        st.markdown("**Live Activity**")

    if not events:
        st.caption("Tool calls will appear here as the agent works.")
    else:
        current_phase = None
        for event in events:
            if event["type"] == "phase_change":
                phase = event["phase"]
                if phase != current_phase:
                    current_phase = phase
                    icon, label = PHASE_LABELS.get(phase, ("▸", phase))
                    st.markdown(
                        f'<div class="phase-badge phase-{phase}">{icon} {label.upper()}</div>',
                        unsafe_allow_html=True,
                    )
            elif event["type"] == "tool_call":
                preview = event.get("result_preview", "")
                st.markdown(
                    f'<div class="tool-row">'
                    f'<span class="tool-num">#{event["number"]}</span>'
                    f'<div>'
                    f'<div class="tool-name">{event["name"]}</div>'
                    f'<div class="tool-preview">{preview[:120]}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

    # Progress bar
    if events:
        phase_events = [e for e in events if e["type"] == "phase_change"]
        if phase_events:
            latest_phase = phase_events[-1]["phase"]
            phase_num = PHASE_ORDER.index(latest_phase) + 1
            progress = phase_num / len(PHASE_ORDER) if is_running else 1.0
            st.progress(progress, text=f"Phase {phase_num}/{len(PHASE_ORDER)}: {latest_phase}")

    if error:
        st.error(f"Error: {error}")

# ── Right: report ──────────────────────────────────────────────────────────────
with col_right:
    st.markdown("**Research Report**")

    # Check outputs/ for the newest file written by file_write tool
    output_files = sorted(
        glob.glob("outputs/*.md") + glob.glob("outputs/*.txt"),
        key=os.path.getmtime,
        reverse=True,
    )
    output_files = [
        f for f in output_files
        if os.path.basename(f) not in ("outline.txt", "scrape_log.txt", "run_log.txt", "run_log_err.txt", ".gitkeep")
    ]
    latest_file = output_files[0] if output_files else None

    if is_running:
        st.info("Report will appear here when the agent finishes...")
        if latest_file:
            st.caption(f"Intermediate file detected: `{latest_file}` — will display when run completes.")

    elif latest_file:
        with open(latest_file, "r", encoding="utf-8", errors="replace") as f:
            file_content = f.read()

        tab1, tab2 = st.tabs(["Rendered", "Raw Markdown"])
        with tab1:
            st.markdown(file_content)
        with tab2:
            st.code(file_content, language="markdown")

        col_dl, col_info = st.columns([1, 2])
        with col_dl:
            st.download_button(
                "Download Report",
                data=file_content,
                file_name=os.path.basename(latest_file),
                mime="text/markdown",
                type="primary",
            )
        with col_info:
            st.caption(f"Saved as `{latest_file}`")

        if report_text:
            with st.expander("Agent summary"):
                st.write(report_text)

    elif report_text:
        st.markdown(report_text)

    else:
        st.caption("Enter a research question above and click **Research →** to begin.")

# ── Auto-refresh while running ─────────────────────────────────────────────────
if is_running:
    time.sleep(0.8)
    st.rerun()
