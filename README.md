# AlphaAgentsV2

> Rebuilding BlackRock's AlphaAgents paper with an eval methodology I actually trust.

I got interested in AlphaAgents — a role-based multi-agent LLM system for picking stocks — but the more I read it the more the evaluation bothered me: look-ahead contamination, no real controls, a tiny single-sector sample, and debate/bias-mitigation claims that were never actually measured. So I'm rebuilding the architecture from scratch with controls that hold up. Full rationale in [DESIGN.md](DESIGN.md).

Status: early scaffolding. Architecture's locked in, data sources and model config aren't final.

- Runs entirely on local open-weight LLMs via [Ollama](https://ollama.com) — no API keys, no per-call cost
- Different agent roles run on different model families (Llama, Qwen, Mistral, Gemma, DeepSeek) — see `config/models.py`
- Price/volume data via `yfinance`, backtest metrics via `pandas`/`numpy`

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env

# Install Ollama (https://ollama.com), then:
ollama serve
ollama pull llama3.1:8b   # at minimum, for the Valuation Agent
```

## Usage

Only the Valuation Agent is wired up end to end so far:

```bash
python -m scripts.analyze AAPL
python -m scripts.analyze AAPL --as-of 2026-06-01 --risk-profile risk_averse
```

Everything else (Fundamental, Sentiment, Macro, Verifier, Red Team, and the debate loop) still throws `NotImplementedError` — see DESIGN.md's Status section.

Tests: `pytest`

## Desktop app

A proper UI instead of the CLI — Electron + React, talking to a local FastAPI
backend that Electron spawns and manages for you (no manual `uvicorn`
command). Shows the full six-agent roster; agents that aren't wired up yet
show their real backend error rather than a fake result.

```bash
pip install -r requirements.txt   # backend deps, if you haven't already

cd frontend
npm install
npm run electron:dev
```

See [DESIGN.md](DESIGN.md#desktop-app-frontend) for the visual direction and
architecture notes.

## Layout

- `agents/` — agent role implementations + shared base class
- `data/` — point-in-time data loaders (prices, filings, news)
- `debate/` — multi-agent orchestration, structured debate/consensus
- `backtest/` — portfolio construction, Black-Litterman, performance metrics
- `config/` — risk profiles, universe definitions, per-agent model assignments
- `backend/` — local FastAPI service for the desktop app
- `frontend/` — Electron + React desktop app
