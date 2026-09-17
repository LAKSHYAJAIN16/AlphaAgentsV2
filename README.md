# AlphaAgentsV2

A role-based multi-agent LLM system for equity stock selection — a redesign
of BlackRock's [AlphaAgents](https://arxiv.org/abs/2508.11152) (Zhao et al.,
2025) that fixes the original's evaluation methodology (look-ahead
contamination, no controls, tiny single-sector sample, unmeasured debate and
bias-mitigation claims) rather than just reproducing its architecture.

See [DESIGN.md](DESIGN.md) for the full rationale and what's different from
the original paper.

## Status

Early scaffolding — architecture and design decided, data sources and model
config not yet finalized.

## Tech stack

- Python 3.11, pytest + ruff
- Open-weight LLMs run locally via [Ollama](https://ollama.com) — different
  agent roles run on different model families (Llama, Qwen, Mistral, Gemma,
  DeepSeek), see `config/models.py`. No API keys, no cost.
- `yfinance` for price/volume data, `pandas`/`numpy` for backtest metrics

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env

# Install Ollama (https://ollama.com), then run it and pull the models
# assigned in config/models.py:
ollama serve
ollama pull llama3.1:8b   # at minimum, for the Valuation Agent
```

## Run it

Only the Valuation Agent is wired up end-to-end so far — real price data,
real local model call:

```bash
python -m scripts.analyze AAPL
python -m scripts.analyze AAPL --as-of 2026-06-01 --risk-profile risk_averse
```

Everything else (Fundamental/Sentiment/Macro/Verifier/Red Team, and the
debate loop) is still `NotImplementedError` pending their data loaders —
see DESIGN.md's Status section.

## Tests

```bash
pytest
```

## Layout

- `agents/` — agent role implementations (Fundamental, Sentiment, Valuation,
  Macro, Verifier, Red Team) + shared base class
- `data/` — point-in-time data loaders (prices, filings, news)
- `debate/` — multi-agent orchestration and structured debate/consensus
- `backtest/` — portfolio construction, Black-Litterman view combination,
  performance metrics with statistical significance testing
- `config/` — risk-tolerance profiles, universe definitions, per-agent model
  assignments
- `tests/`
