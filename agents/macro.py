from datetime import date

from agents.base import Agent, AgentAnalysis

ROLE_PROMPT = """As a macro strategist, your primary responsibility is to
analyze the prevailing interest-rate environment, sector rotation trends,
and macroeconomic regime as of the given date, and assess their likely
impact on the given security's sector. This role does not exist in the
original AlphaAgents paper — it was added because the paper's agents never
reason about regime context, which likely contributed to its risk-averse
portfolios underperforming during a sector-wide bull run they had no way to
anticipate."""


class MacroAgent(Agent):
    role = "macro"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        # TODO: wire to a macro data source (rates, sector ETF flows) —
        # not yet selected, see DESIGN.md open questions.
        raise NotImplementedError("macro data loader not yet implemented")
