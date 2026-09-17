from datetime import date

from agents.base import Agent, AgentAnalysis

ROLE_PROMPT = """As a sentiment equity analyst, your primary responsibility
is to analyze financial news, analyst ratings, and disclosures related to
the given security, using only items dated on or before the given date.
Summarize the prevailing sentiment and its likely implication for the stock
price, and cite the specific article/rating for every material claim. Flag
explicitly when news coverage is too thin to support a confident call —
report low conviction rather than filling the gap with general knowledge."""


class SentimentAgent(Agent):
    role = "sentiment"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        # TODO: wire to data/news.py (point-in-time news loader, not yet
        # implemented — requires a news API key, see .env.example).
        raise NotImplementedError("news data loader not yet implemented")
