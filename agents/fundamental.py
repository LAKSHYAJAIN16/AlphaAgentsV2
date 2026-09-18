from datetime import date

from agents.base import Agent, AgentAnalysis, Citation, Recommendation
from agents.llm_client import call_model, parse_structured_response
from data.filings import find_latest_filing, load_filing_text

ROLE_PROMPT = """As a fundamental financial equity analyst, your primary
responsibility is to analyze the most recent 10-K/10-Q filing for a company
as of the given date, using only the filing text provided to you. Base your
analysis solely on that text — name the specific section you drew from
(e.g. "Item 7: MD&A", "Item 1A: Risk Factors") for every material claim, so
it can be checked before entering debate. Do not rely on general knowledge
about the company beyond what the filing text supports; if you recognize
the company, treat that recognition as a bias risk, not evidence."""

RESPONSE_FORMAT = (
    'Respond with ONLY a JSON object, no other text: '
    '{"recommendation": "BUY" | "SELL" | "HOLD", "conviction": <0-10 number>, '
    '"reasoning": "<2-4 sentences>", "cited_section": "<section name, e.g. Item 7: MD&A>"}'
)


class FundamentalAgent(Agent):
    role = "fundamental"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        filing = find_latest_filing(ticker, as_of)
        filing_text = load_filing_text(filing)

        user_prompt = (
            f"Ticker: {ticker}\n"
            f"As of: {as_of.isoformat()}\n"
            f"Filing: {filing.form} filed {filing.filing_date.isoformat()}\n\n"
            f"--- FILING TEXT (truncated) ---\n{filing_text}\n--- END FILING TEXT ---\n\n"
            f"Risk profile: {self.risk_profile.name} — {self.risk_profile.description}\n\n"
            f"{RESPONSE_FORMAT}"
        )
        raw = call_model(self.model_config, ROLE_PROMPT, user_prompt)
        parsed = parse_structured_response(raw)

        recommendation = Recommendation(parsed["recommendation"])
        conviction = float(parsed["conviction"])

        return AgentAnalysis(
            agent_role=self.role,
            ticker=ticker,
            as_of=as_of,
            recommendation=recommendation,
            conviction=max(0.0, min(10.0, conviction)),
            reasoning=parsed.get("reasoning", ""),
            citations=[
                Citation(source=filing.source_id, excerpt=parsed.get("cited_section", "(section not named)"))
            ],
            model_tag=self.model_config.as_run_tag(),
        )
