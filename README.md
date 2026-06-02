# Deep Research Agent

An autonomous deep research agent built for the X-ARC Agentic AI Engineer Hackathon.

## Setup

1. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Architecture

- `agent/` — core agent loop, context management, subagent orchestration
- `tools/` — 50+ tools across 4 namespaces (web, file, data, output)
- `models/` — Pydantic schemas for all tool inputs/outputs
- `observability/` — structured logging
- `evals/` — evaluation harness
- `tests/` — unit and integration tests
