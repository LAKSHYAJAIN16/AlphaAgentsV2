"""CLI: run a single agent's analysis against a real ticker.

Valuation, Fundamental, and Sentiment are wired up end-to-end so far. Macro
still raises NotImplementedError pending its data loader — see DESIGN.md.

Usage:
    python -m scripts.analyze AAPL
    python -m scripts.analyze AAPL --role fundamental --as-of 2026-06-01 --risk-profile risk_averse
"""

import argparse
from datetime import date

from dotenv import load_dotenv

from agents.fundamental import FundamentalAgent
from agents.llm_client import ModelCallError
from agents.macro import MacroAgent
from agents.sentiment import SentimentAgent
from agents.valuation import ValuationAgent
from config.models import DEFAULT_AGENT_MODELS
from config.risk_profiles import ALL_PROFILES

AGENTS = {
    "fundamental": FundamentalAgent,
    "sentiment": SentimentAgent,
    "valuation": ValuationAgent,
    "macro": MacroAgent,
}


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument("--role", default="valuation", choices=list(AGENTS))
    parser.add_argument("--as-of", default=date.today().isoformat(), help="YYYY-MM-DD, defaults to today")
    parser.add_argument("--risk-profile", default="risk_neutral", choices=list(ALL_PROFILES))
    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of)
    risk_profile = ALL_PROFILES[args.risk_profile]
    agent_cls = AGENTS[args.role]
    agent = agent_cls(model_config=DEFAULT_AGENT_MODELS[args.role], risk_profile=risk_profile)

    try:
        analysis = agent.analyze(args.ticker.upper(), as_of)
    except (ModelCallError, NotImplementedError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    print(f"{analysis.ticker} @ {analysis.as_of} ({risk_profile.name}, {args.role})")
    print(f"  Recommendation: {analysis.recommendation.value}")
    print(f"  Conviction:     {analysis.conviction:.1f}/10")
    print(f"  Reasoning:      {analysis.reasoning}")
    for c in analysis.citations:
        print(f"  Citation:       [{c.source}] {c.excerpt}")
    print(f"  Model:          {analysis.model_tag}")


if __name__ == "__main__":
    main()
