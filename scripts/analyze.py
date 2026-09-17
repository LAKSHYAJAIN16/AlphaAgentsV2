"""CLI: run a single agent's analysis against a real ticker.

Only the Valuation Agent is wired up end-to-end so far (it needs just
price data, which is free via yfinance). Fundamental/Sentiment/Macro still
raise NotImplementedError pending their data loaders — see DESIGN.md.

Usage:
    python -m scripts.analyze AAPL
    python -m scripts.analyze AAPL --as-of 2026-06-01 --risk-profile risk_averse
"""

import argparse
from datetime import date

from agents.llm_client import ModelCallError
from agents.valuation import ValuationAgent
from config.models import DEFAULT_AGENT_MODELS
from config.risk_profiles import ALL_PROFILES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument("--as-of", default=date.today().isoformat(), help="YYYY-MM-DD, defaults to today")
    parser.add_argument("--risk-profile", default="risk_neutral", choices=list(ALL_PROFILES))
    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of)
    risk_profile = ALL_PROFILES[args.risk_profile]
    agent = ValuationAgent(model_config=DEFAULT_AGENT_MODELS["valuation"], risk_profile=risk_profile)

    try:
        analysis = agent.analyze(args.ticker.upper(), as_of)
    except ModelCallError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"{analysis.ticker} @ {analysis.as_of} ({risk_profile.name})")
    print(f"  Recommendation: {analysis.recommendation.value}")
    print(f"  Conviction:     {analysis.conviction:.1f}/10")
    print(f"  Reasoning:      {analysis.reasoning}")
    for c in analysis.citations:
        print(f"  Citation:       [{c.source}] {c.excerpt}")
    print(f"  Model:          {analysis.model_tag}")


if __name__ == "__main__":
    main()
