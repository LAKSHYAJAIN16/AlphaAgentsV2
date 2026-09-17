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

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in API keys
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
