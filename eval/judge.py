#!/usr/bin/env python3
"""
eval/judge.py — LLM-as-judge evaluation harness for due diligence reports.

Scores a completed report on 5 criteria and saves a formatted scorecard.

Usage:
    python eval/judge.py                      # scores newest file in outputs/
    python eval/judge.py outputs/report.md    # scores a specific file
"""

import os
import sys
import glob
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CRITERIA = {
    "completeness": (
        "Does the report cover all major due diligence areas: financials, corporate governance, "
        "legal/regulatory exposure, market position, and strategic risks?"
    ),
    "data_accuracy": (
        "Are financial figures and factual claims backed by named, cited sources? "
        "Are specific numbers present rather than vague statements?"
    ),
    "risk_coverage": (
        "Are material risks (financial, legal, operational, market) identified, "
        "described with enough detail, and rated or prioritized by severity?"
    ),
    "structure": (
        "Is the report well-organized with clear sections, professional language, "
        "and easy to navigate for an executive reader?"
    ),
    "actionability": (
        "Does the report deliver a clear acquisition recommendation or verdict? "
        "Does it identify conditions, red flags, or concrete next steps?"
    ),
}

JUDGE_PROMPT = """\
You are a senior M&A analyst reviewing a due diligence report for acquisition assessment.
Score the report on 5 criteria from 0 to 10.

Scoring guide:
- 9-10: Excellent — criterion fully met with strong evidence
- 7-8:  Good — criterion mostly met, minor gaps only
- 5-6:  Adequate — criterion partially met
- 3-4:  Weak — criterion barely addressed
- 0-2:  Failing — criterion not met at all

REPORT TO EVALUATE:
---
{report}
---

CRITERIA TO SCORE:
{criteria_block}

Respond ONLY in valid JSON with no other text before or after:
{{
  "scores": {{
    "completeness":  {{"score": 0, "reason": "one or two sentences"}},
    "data_accuracy": {{"score": 0, "reason": "one or two sentences"}},
    "risk_coverage": {{"score": 0, "reason": "one or two sentences"}},
    "structure":     {{"score": 0, "reason": "one or two sentences"}},
    "actionability": {{"score": 0, "reason": "one or two sentences"}}
  }},
  "overall_verdict": "PASS",
  "summary": "two or three sentence overall assessment"
}}

overall_verdict must be one of: PASS (avg >= 7), BORDERLINE (avg 5-6), FAIL (avg < 5)
"""



def _find_report(path_arg: str | None) -> Path:
    """Resolve which report file to evaluate."""
    if path_arg:
        p = Path(path_arg)
        if not p.exists():
            print(f"Error: file not found: {path_arg}")
            sys.exit(1)
        return p

    skip = {".gitkeep", "outline.txt", "scrape_log.txt", "run_log.txt",
            "run_log_err.txt", "placeholder.txt", "debug.txt"}
    files = [
        f for f in glob.glob("outputs/*.md") + glob.glob("outputs/*.txt")
        if Path(f).name not in skip
        and not Path(f).name.startswith("eval_")
    ]
    if not files:
        print("No report files found in outputs/. Run the agent first.")
        sys.exit(1)
    return Path(max(files, key=os.path.getmtime))


def _all_clients():
    """Yield (client, model, provider_name) for every configured provider."""
    candidates = [
        (
            "gemini",
            os.getenv("GEMINI_API_KEY"),
            "https://generativelanguage.googleapis.com/v1beta/openai/",
            "gemini-2.0-flash",
        ),
        (
            "groq-quality",
            os.getenv("GROQ_API_KEY"),
            "https://api.groq.com/openai/v1",
            "llama-3.3-70b-versatile",
        ),
        (
            "groq-fast",
            os.getenv("GROQ_API_KEY"),
            "https://api.groq.com/openai/v1",
            "llama-3.1-8b-instant",
        ),
        (
            "cerebras",
            os.getenv("CEREBRAS_API_KEY"),
            "https://api.cerebras.ai/v1",
            "gpt-oss-120b",
        ),
    ]
    for name, key, base_url, model in candidates:
        if key:
            yield OpenAI(api_key=key, base_url=base_url), model, name


def _call_judge(report_text: str) -> dict:
    """Call the LLM judge and return parsed JSON result. Falls back across providers."""
    from openai import RateLimitError

    criteria_block = "\n".join(
        f"- {name}: {desc}" for name, desc in CRITERIA.items()
    )
    prompt = JUDGE_PROMPT.format(
        report=report_text[:6000],
        criteria_block=criteria_block,
    )

    for client, model, provider in _all_clients():
        print(f"  Trying judge: {provider} / {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
        except RateLimitError:
            print(f"  {provider} rate limited — trying next provider...")
            continue

        raw = response.choices[0].message.content.strip()

        # Extract JSON block — find outermost { } in case the model adds surrounding text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print(f"  {provider} returned malformed JSON — trying next provider...")
            continue

    print("\nAll providers exhausted or returned bad JSON.")
    sys.exit(1)


def _render_scorecard(result: dict, report_path: Path) -> str:
    """Format eval result as a readable markdown scorecard."""
    scores = result["scores"]
    total = sum(v["score"] for v in scores.values())
    max_score = len(scores) * 10
    pct = round(total / max_score * 100)

    verdict = result.get("overall_verdict", "UNKNOWN")
    verdict_icon = {"PASS": "✅", "BORDERLINE": "⚠️", "FAIL": "❌"}.get(verdict, "❓")

    lines = [
        "# Due Diligence Report — Evaluation Scorecard",
        "",
        f"**Report:** `{report_path}`",
        f"**Verdict:** {verdict_icon} {verdict}",
        f"**Total score:** {total} / {max_score} ({pct}%)",
        "",
        "## Criterion Breakdown",
        "",
        "| Criterion | Score | Reasoning |",
        "|-----------|:-----:|-----------|",
    ]

    for name, data in scores.items():
        filled = "█" * data["score"]
        empty = "░" * (10 - data["score"])
        label = name.replace("_", " ").title()
        lines.append(
            f"| **{label}** | {data['score']}/10 `{filled}{empty}` | {data['reason']} |"
        )

    lines += [
        "",
        "## Overall Assessment",
        "",
        result.get("summary", ""),
        "",
        "---",
        f"*Evaluated by LLM-as-judge · Due Diligence Agent eval harness*",
    ]

    return "\n".join(lines)


def main():
    report_path = _find_report(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"Evaluating: {report_path}")

    report_text = report_path.read_text(encoding="utf-8", errors="replace")

    result = _call_judge(report_text)
    scorecard = _render_scorecard(result, report_path)

    # Print safely — Windows terminals may not support emoji
    try:
        print("\n" + scorecard)
    except UnicodeEncodeError:
        print("\n" + scorecard.encode("ascii", errors="replace").decode("ascii"))

    eval_path = Path("outputs") / f"eval_{report_path.stem}.md"
    eval_path.write_text(scorecard, encoding="utf-8")
    print(f"\nSaved to: {eval_path}")


if __name__ == "__main__":
    main()
