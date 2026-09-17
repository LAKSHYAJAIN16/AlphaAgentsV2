"""Shared agent interface.

Every agent role produces the same structured output shape so the debate
layer can compare, cite, and aggregate them mechanically instead of parsing
free-text chat (which is what the original paper's raw AutoGen group chat
does). Conviction is a required numeric field, not implicit in wording —
needed both for Black-Litterman position sizing (backtest/) and for the
quantified risk-profile thresholds (config/risk_profiles.py).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from config.models import ModelConfig
from config.risk_profiles import RiskProfile


class Recommendation(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class Citation:
    """A grounding pointer back to a source document/data point.

    Required on every claim that reaches the Verifier Agent — see
    debate/protocol.py. This is what makes faithfulness checkable instead of
    asserted.
    """

    source: str  # e.g. "10-K:Item 7:MD&A" or "yfinance:AAPL:2026-02-01"
    excerpt: str


@dataclass
class AgentAnalysis:
    agent_role: str
    ticker: str
    as_of: date
    recommendation: Recommendation
    conviction: float  # 0-10, required — see module docstring
    reasoning: str
    citations: list[Citation] = field(default_factory=list)
    model_tag: str = ""  # ModelConfig.as_run_tag(), for reproducibility logs

    def __post_init__(self) -> None:
        if not 0.0 <= self.conviction <= 10.0:
            raise ValueError(f"conviction must be in [0, 10], got {self.conviction}")


class Agent(ABC):
    """Base class for a specialist analyst agent.

    Subclasses declare what data they're allowed to see (per Table 1 of the
    original paper — each agent only gets the data relevant to its role) and
    implement `analyze`.
    """

    role: str

    def __init__(self, model_config: ModelConfig, risk_profile: RiskProfile) -> None:
        self.model_config = model_config
        self.risk_profile = risk_profile

    @abstractmethod
    def analyze(self, ticker: str, as_of: date) -> AgentAnalysis:
        """Produce a structured analysis as of a given date.

        `as_of` is enforced point-in-time: implementations must not use data
        dated after this value. See data/ loaders, which take `as_of` and
        filter accordingly — this is the mechanism that fixes the original
        paper's look-ahead risk.
        """
        raise NotImplementedError
