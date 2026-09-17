from datetime import date

from agents.base import Agent, AgentAnalysis, Citation, Recommendation
from agents.llm_client import call_model, parse_structured_response
from backtest.metrics import annualized_volatility, cumulative_return
from data.prices import load_price_history

ROLE_PROMPT = """As a valuation equity analyst, your primary responsibility
is to analyze the historical price/volume trends of the given security up to
and including the given date, using the computed volatility/return figures
provided to you rather than estimating them yourself. Your recommendation
must respect your assigned risk profile's maximum accepted volatility and
minimum conviction thresholds."""

RESPONSE_FORMAT = (
    'Respond with ONLY a JSON object, no other text: '
    '{"recommendation": "BUY" | "SELL" | "HOLD", "conviction": <0-10 number>, '
    '"reasoning": "<2-4 sentences>"}'
)


class ValuationAgent(Agent):
    role = "valuation"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        prices = load_price_history(ticker, as_of)
        daily_returns = prices["Close"].pct_change().dropna().to_numpy().flatten()
        volatility = annualized_volatility(daily_returns)
        cum_return = cumulative_return(daily_returns)

        user_prompt = (
            f"Ticker: {ticker}\n"
            f"As of: {as_of.isoformat()}\n"
            f"Trailing ~6mo annualized volatility: {volatility:.2%}\n"
            f"Trailing ~6mo cumulative return: {cum_return:.2%}\n"
            f"Risk profile: {self.risk_profile.name} — {self.risk_profile.description}\n\n"
            f"{RESPONSE_FORMAT}"
        )
        raw = call_model(self.model_config, ROLE_PROMPT, user_prompt)
        parsed = parse_structured_response(raw)

        recommendation = Recommendation(parsed["recommendation"])
        conviction = float(parsed["conviction"])

        # Programmatic enforcement of the risk profile's volatility cap —
        # the role prompt asks the model to respect it, but this doesn't
        # rely on the model actually doing so.
        if recommendation == Recommendation.BUY and volatility > self.risk_profile.max_accepted_volatility:
            recommendation = Recommendation.HOLD
            conviction = min(conviction, self.risk_profile.min_conviction_to_buy - 0.1)

        return AgentAnalysis(
            agent_role=self.role,
            ticker=ticker,
            as_of=as_of,
            recommendation=recommendation,
            conviction=max(0.0, min(10.0, conviction)),
            reasoning=parsed.get("reasoning", ""),
            citations=[
                Citation(
                    source=f"yfinance:{ticker}:{as_of.isoformat()}",
                    excerpt=f"annualized_volatility={volatility:.2%}, cumulative_return={cum_return:.2%}",
                )
            ],
            model_tag=self.model_config.as_run_tag(),
        )
