# AlphaAgentsV2 — Design

Reimplementation of BlackRock's AlphaAgents (Zhao et al., 2025) — a role-based
multi-agent LLM system for equity stock selection — fixing the methodological
gaps in the original paper rather than just reproducing it.

## What the original paper got right

- Role specialization (Fundamental / Sentiment / Valuation agents) each with
  their own data access and tools.
- Structured debate/consensus mechanism to reconcile disagreement between
  agents before a final call.
- Explicit risk-tolerance conditioning via role prompts.

## What it got wrong, and what this project does instead

| Gap in AlphaAgents | Fix in AlphaAgentsV2 |
|---|---|
| Single model (GPT-4o) talking to itself across all agent roles | Model-heterogeneous agents — different agent roles can run on different model families, so debate isn't one model agreeing with itself in different voices |
| No look-ahead control — backtest window (Feb–Jun 2024) overlaps GPT-4o's training data, so "prediction" may just be memorization | Point-in-time data enforcement: agents only see filings/news dated before the decision date; backtests run on windows after the model's training cutoff; a blinded-ticker ablation checks whether recommendations lean on brand recognition instead of the actual filing |
| 15 stocks, one sector, one 4-month bull-market window | Multi-sector universe (stratified by sector/size/style), multiple disjoint regimes (bear/sideways/bull), true market-cap benchmark instead of a self-referential subset |
| No single-agent control — never tests whether multi-agent debate actually beats one agent with all the same data | Explicit control: one agent, all tools, no role split, no debate — multi-agent must beat this to justify its complexity |
| No hallucination/debate ablation — "reduces hallucination" is asserted via citation, never measured for their own system | Direct A/B: same stock/day, debate on vs. off; log convergence rate, rounds-to-consensus, how often debate flips the initial call |
| Cognitive-bias-mitigation is the paper's core motivation (Kahneman/Tversky) but never tested | Explicit bias probes (recency/anchoring after a run-up, disposition-effect reluctance to sell a loser); a dedicated Red Team agent whose only job is to argue the opposite side |
| Binary BUY/SELL, equal-weighted — not actually "portfolio construction" | Numeric conviction elicited per agent; used as Black-Litterman views against a market-equilibrium prior for real position sizing |
| No statistical significance testing, single-path Sharpe plots | Multiple seeds per backtest, bootstrap confidence intervals on Sharpe/returns |
| Risk-seeking profile dropped as "indistinguishable from risk-neutral," never investigated | Quantified risk lens (explicit thresholds the agent must reason against) instead of adjective-only role prompts |
| No cost/latency/reproducibility reporting | Pinned model versions + decoding params logged per run; cost and wall-clock time reported per stock analyzed |

## Agent roster

- **Fundamental Agent** — 10-K/10-Q analysis (SEC EDGAR), same role as original
- **Sentiment Agent** — news/analyst-rating analysis
- **Valuation Agent** — price/volume technicals, volatility/return tooling
- **Macro Agent** *(new)* — rates, sector rotation, macro regime context
- **Verifier Agent** *(new)* — grounds every claim from the other agents in a
  citation before it's allowed into debate
- **Red Team Agent** *(new)* — structurally required to argue against the
  emerging consensus; operationalizes the bias-mitigation claim instead of
  asserting it

## Repo layout

```
agents/       agent role implementations + base class
data/         point-in-time data loaders (prices, filings, news)
debate/       orchestration, structured debate protocol, consensus logic
backtest/     portfolio construction, Black-Litterman combination, metrics
config/       risk profiles, universe definitions, model assignments
tests/
```

## Open questions / not yet decided

- Point-in-time filings data source (SEC EDGAR full-text search is free but
  needs its own point-in-time discipline; vendor data would be cleaner but
  costs money)
- News/sentiment data source and API budget
- Which additional model families to run alongside Claude for heterogeneity
