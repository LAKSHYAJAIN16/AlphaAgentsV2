# AlphaAgentsV2

I got interested in BlackRock's AlphaAgents paper — a role-based multi-agent
LLM system for picking stocks — but the more I read it the more the
evaluation bothered me: look-ahead contamination, no real controls, a tiny
single-sector sample, and debate/bias-mitigation claims that were never
actually measured. So instead of just reproducing their architecture, I'm
rebuilding it with an eval methodology I actually trust. The full rationale
is in [DESIGN.md](DESIGN.md) if you want the details on what's different
from the original paper.

## Where it's at

Early scaffolding. Architecture and design are locked in, but data sources
and model config aren't finalized yet.

## How it's built

Everything runs on open-weight LLMs locally via [Ollama](https://ollama.com)
— no API keys, no per-call cost. Different agent roles run on different
model families (Llama, Qwen, Mistral, Gemma, DeepSeek) — see
`config/models.py` for the assignments. Price/volume data comes from
`yfinance`, `pandas`/`numpy` handle the backtest metrics. Python 3.11,
tested with pytest, linted with ruff.

## Getting it running

```bash
pip install -r requirements.txt
cp .env.example .env

# Install Ollama (https://ollama.com), then:
ollama serve
ollama pull llama3.1:8b   # at minimum, for the Valuation Agent
```

Right now only the Valuation Agent is wired up end to end — real price
data, real local model call:

```bash
python -m scripts.analyze AAPL
python -m scripts.analyze AAPL --as-of 2026-06-01 --risk-profile risk_averse
```

Everything else (Fundamental, Sentiment, Macro, Verifier, Red Team, and the
actual debate loop) still throws `NotImplementedError` while I build out
their data loaders — see DESIGN.md's Status section for where each one
stands.

Tests: `pytest`

## What's where

- `agents/` — the agent role implementations (Fundamental, Sentiment,
  Valuation, Macro, Verifier, Red Team) plus a shared base class
- `data/` — point-in-time data loaders (prices, filings, news)
- `debate/` — multi-agent orchestration and the structured debate/consensus
  logic
- `backtest/` — portfolio construction, Black-Litterman view combination,
  performance metrics with significance testing
- `config/` — risk-tolerance profiles, universe definitions, per-agent
  model assignments
- `tests/`
