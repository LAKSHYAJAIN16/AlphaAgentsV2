from datetime import date

from agents.base import Agent, AgentAnalysis

ROLE_PROMPT = """You are an equity analyst with access to fundamental
filings, financial news, and price/volume history for the given security as
of the given date. Produce a single BUY/SELL/HOLD recommendation with a
conviction score, citing your evidence.

This is the control baseline the original AlphaAgents paper never ran: one
agent, all the same data and tools the specialist agents get, no role
split, no debate. If the multi-agent debate framework (debate/orchestrator.py)
doesn't outperform this control on the same backtest windows, the added
complexity isn't earning its keep."""


class SingleAgentControl(Agent):
    role = "single_agent_control"

    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        # TODO: wire to all three data loaders (filings, news, prices) once
        # they exist, single model call, no debate.
        raise NotImplementedError("data loaders not yet implemented")
