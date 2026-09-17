from datetime import date

from agents.base import Agent, AgentAnalysis

ROLE_PROMPT = """As a valuation equity analyst, your primary responsibility
is to analyze the historical price/volume trends of the given security up to
and including the given date. Use the provided volatility/return
calculation tool rather than estimating these figures yourself. Your
recommendation must respect your assigned risk profile's maximum accepted
volatility and minimum conviction thresholds — if the computed annualized
volatility exceeds your profile's cap, you may not recommend BUY regardless
of momentum."""


class ValuationAgent(Agent):
    role = "valuation"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        # TODO: wire to data/prices.py (yfinance point-in-time loader) and
        # the annualized return/volatility tool described in DESIGN.md.
        raise NotImplementedError("price data loader not yet implemented")
