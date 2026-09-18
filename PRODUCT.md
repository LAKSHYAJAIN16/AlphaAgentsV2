# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Electron desktop app wrapping a React/TypeScript renderer. The renderer talks
to a local Python backend (FastAPI) that the Electron main process spawns and
manages automatically — the user never runs a Python command by hand. User
specified Electron + a JS/React frontend explicitly; FastAPI backend choice is
delegated (chosen for the existing Python agent code in `agents/`, `backtest/`,
`config/`).

## Users

The developer/researcher building this (a student doing independent equity-
research/behavioral-finance research under academic mentorship), running
analyses against a research prototype. Described by the user as "a research
project" — treat the audience as the researcher themselves plus occasional
review by a mentor or others evaluating the research, not a general public
product. Credibility as a serious research tool matters more than consumer
polish or onboarding flourish.

## Product Purpose

A desktop app front-end for AlphaAgentsV2 — a role-based multi-agent LLM
system for equity stock analysis, built as a methodologically-corrected
reimplementation of BlackRock's AlphaAgents paper. The app lets the user
enter a ticker, a risk-tolerance profile, and an as-of date, and see each
specialist agent's analysis (recommendation, conviction score, reasoning,
citations) without touching the command line.

## Positioning

Unlike the original AlphaAgents paper (single closed model playing every
role, unmeasured debate/bias claims, no look-ahead controls — see
DESIGN.md), this system runs genuinely heterogeneous open-weight models per
agent role via Ollama, enforces point-in-time data, and is built to make the
multi-agent debate's actual value measurable rather than asserted. The
desktop app is the visible surface of that research methodology, not a
trading product.

## Operating Context

Runs locally on the user's own machine. Requires Ollama running with the
models assigned in `config/models.py` pulled locally; no cloud API keys.
The user's other research/dev tools are plain code editors and terminals —
this app is meant to replace typing `python -m scripts.analyze TICKER` by
hand, not to compete with a trading terminal.

## Capabilities and Constraints

- Confirmed working today: Valuation Agent only (real yfinance price data +
  local Ollama model call). Fundamental, Sentiment, Macro, Verifier, Red
  Team, and the full debate loop are implemented as typed interfaces that
  currently raise `NotImplementedError` pending their data loaders.
- User decision: the UI shows the full six-agent roster now, with
  not-yet-wired agents clearly marked as such, rather than hiding them
  until implemented — the UI is meant to grow into the backend as agents
  come online, not be redesigned each time one is added.
- No user accounts, no persistence/history requirement established yet
  (undecided — do not invent a saved-analyses feature).
- No real trading or order execution of any kind — analysis/research
  output only.

## Evidence on Hand

None (no existing screenshots, logos, or brand assets). Backend code,
DESIGN.md, and README.md in this repo are the factual source for what the
system actually does — do not describe capabilities beyond what's in
DESIGN.md's Status section.

## Product Principles

1. Show the system's actual state honestly — an agent that isn't wired up
   yet reads as "not implemented," never as a fake/placeholder result.
2. Analytical, not decorative — the tool's credibility as research comes
   from precision (real numbers, real citations, real model identifiers),
   not from visual flourish standing in for substance.
3. The desktop app is a thin, honest window onto the Python backend's real
   state — it queries the backend itself (auto-spawned), never fabricates
   or caches fake data client-side.
4. Built to grow — the six-agent layout and debate view are designed for
   the full roster this project is building toward, not just today's
   single working agent.
