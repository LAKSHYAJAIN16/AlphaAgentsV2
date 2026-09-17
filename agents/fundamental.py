from datetime import date

from agents.base import Agent, AgentAnalysis

ROLE_PROMPT = """As a fundamental financial equity analyst, your primary
responsibility is to analyze the most recent 10-K/10-Q filings for a company
as of the given date, using only filings dated on or before that date. Base
your analysis solely on retrieved filing text — cite the specific section
(e.g. "Item 7: MD&A", "Item 1A: Risk Factors") for every material claim, so
it can be checked by the Verifier Agent before entering debate. Do not rely
on general knowledge about the company beyond what the retrieved filing
supports; if you recognize the company, treat that recognition as a bias
risk, not evidence."""


class FundamentalAgent(Agent):
    role = "fundamental"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        # TODO: wire to data/filings.py (SEC EDGAR point-in-time loader,
        # not yet implemented) + RAG retrieval tool, then call
        # self.model_config's provider with ROLE_PROMPT.
        raise NotImplementedError("filings data loader not yet implemented")
