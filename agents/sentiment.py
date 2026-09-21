from datetime import date

from agents.base import Agent, AgentAnalysis, Citation, Recommendation
from agents.llm_client import call_model, parse_structured_response
from data.news import load_company_news

ROLE_PROMPT = """As a sentiment equity analyst, your primary responsibility
is to analyze financial news, analyst ratings, and disclosures related to
the given security, using only items dated on or before the given date.
Summarize the prevailing sentiment and its likely implication for the stock
price, and cite the specific article/rating for every material claim. Flag
explicitly when news coverage is too thin to support a confident call —
report low conviction rather than filling the gap with general knowledge."""

RESPONSE_FORMAT = (
    'Respond with ONLY a JSON object, no other text: '
    '{"recommendation": "BUY" | "SELL" | "HOLD", "conviction": <0-10 number>, '
    '"reasoning": "<2-4 sentences>", "cited_headline": "<headline of the most load-bearing article, or empty string if none>"}'
)

MAX_ARTICLES_IN_PROMPT = 15


class SentimentAgent(Agent):
    role = "sentiment"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        articles = load_company_news(ticker, as_of)
        top_articles = articles[:MAX_ARTICLES_IN_PROMPT]

        if top_articles:
            headlines_block = "\n".join(
                f"- [{a.published.isoformat()}] ({a.source}) {a.headline}: {a.summary}" for a in top_articles
            )
        else:
            headlines_block = "(no news articles found in the lookback window)"

        user_prompt = (
            f"Ticker: {ticker}\n"
            f"As of: {as_of.isoformat()}\n\n"
            f"--- NEWS ITEMS ---\n{headlines_block}\n--- END NEWS ITEMS ---\n\n"
            f"Risk profile: {self.risk_profile.name} — {self.risk_profile.description}\n\n"
            f"{RESPONSE_FORMAT}"
        )
        raw = call_model(self.model_config, ROLE_PROMPT, user_prompt)
        parsed = parse_structured_response(raw)

        recommendation = Recommendation(parsed["recommendation"])
        conviction = float(parsed["conviction"])

        # Coverage this thin can't support a confident call regardless of
        # what the model claims — programmatic floor, not just a prompt ask,
        # matching how ValuationAgent enforces its risk cap in code.
        if not top_articles:
            conviction = min(conviction, 2.0)

        cited_headline = parsed.get("cited_headline") or ""
        matching = next((a for a in top_articles if a.headline == cited_headline), None)
        citation = (
            Citation(source=matching.source_id, excerpt=matching.headline)
            if matching
            else Citation(source=f"Finnhub:{ticker}:{as_of.isoformat()}", excerpt="(no specific article cited)")
        )

        return AgentAnalysis(
            agent_role=self.role,
            ticker=ticker,
            as_of=as_of,
            recommendation=recommendation,
            conviction=max(0.0, min(10.0, conviction)),
            reasoning=parsed.get("reasoning", ""),
            citations=[citation],
            model_tag=self.model_config.as_run_tag(),
        )
