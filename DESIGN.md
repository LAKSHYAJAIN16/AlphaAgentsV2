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
| Single model (GPT-4o) talking to itself across all agent roles | Model-heterogeneous agents on **open-weight models run locally via Ollama** (Llama, Qwen, Mistral, Gemma, DeepSeek) — genuinely different model families per role, not prompt variation on one vendor's model, and free/reproducible to rerun since nothing depends on a closed API |
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
agents/       agent role implementations + base class + Ollama client
data/         point-in-time data loaders (prices, filings, news)
debate/       orchestration, structured debate protocol, consensus logic
backtest/     portfolio construction, Black-Litterman combination, metrics
config/       risk profiles, universe definitions, model assignments
scripts/      CLI entry points
backend/      local FastAPI service the desktop app talks to
frontend/     Electron + React desktop app
tests/
```

## Status

- **Working end-to-end:**
  - Valuation Agent (`agents/valuation.py`) — real yfinance point-in-time
    price data, real Ollama model call, real structured output.
  - Fundamental Agent (`agents/fundamental.py`) — real point-in-time SEC
    EDGAR 10-K/10-Q lookup (`data/filings.py`), real filing text (Inline
    XBRL metadata stripped out — see that module's docstring), real Ollama
    model call. v1 simplification: takes the filing's first ~15k characters
    rather than section-aware retrieval; the "Financial Report RAG Tool"
    the original paper describes is still future work.
  - Sentiment Agent (`agents/sentiment.py`) — real point-in-time news via
    Finnhub's company-news endpoint (`data/news.py`, requires a free
    `FINNHUB_API_KEY`), real Ollama model call. Thin/empty coverage is
    handled explicitly rather than erroring: the prompt asks for low
    conviction on sparse news, and a programmatic cap enforces it when no
    articles are found at all, mirroring how ValuationAgent enforces its
    volatility cap in code rather than trusting the model.
  - Run either via `python -m scripts.analyze TICKER --role {valuation,fundamental,sentiment}`
    (CLI) or the desktop app (`frontend/`, see below).
- **Stubbed (`NotImplementedError`):** Macro, Verifier, Red Team,
  single-agent control, and the debate round-robin loop — Macro still needs
  a data source decision (see Open questions below); Verifier/Red Team/
  single-agent control/debate need the rest of the roster in place first.
  The desktop app surfaces these as "not implemented" using the backend's
  real `NotImplementedError` text, not a fake placeholder result.

## Desktop app (`frontend/`)

Electron + React/TypeScript, talking to `backend/api.py` (FastAPI) over
localhost HTTP. The Electron main process (`frontend/electron/main.cjs`)
spawns the Python backend automatically on launch and kills it on quit — the
user never runs a Python command by hand.

Visual direction: a research-terminal aesthetic (Bloomberg/EDGAR/lab-notebook
lineage) chosen deliberately against the generic "AI SaaS dashboard" look —
near-black ground, restrained neutral palette with one signal-amber accent
for actions/focus, semantic green/red reserved strictly for BUY/SELL
recommendations, IBM Plex Mono for tickers/model-tags/citations. Every agent
card shows its real backend state (a working result, a genuine
`NotImplementedError` message, or "debate-only" for roles that don't run
standalone) — color is never the only signal, every state also carries a
text pill.

Run it:
```bash
cd frontend
npm install
npm run electron:dev
```
This starts the Vite dev server, waits for it, then launches Electron
pointed at it (which in turn spawns the Python backend from the repo root —
run `pip install -r requirements.txt` there first).

## Open questions / not yet decided

- Section-aware retrieval for filings (currently first-~15k-characters
  truncation — see Fundamental Agent above)
- Macro data source (rates, sector ETF flows) — not yet selected
- Local compute for the larger assigned models (e.g. `deepseek-r1:14b`,
  `mixtral:8x7b`) — may need to downgrade to smaller quantized variants
  depending on available RAM/VRAM
