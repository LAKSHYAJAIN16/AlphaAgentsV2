"""Verifier and Red Team agents, and the structured debate record.

Neither of these is a data-sourcing analyst (agents/), so neither subclasses
Agent from agents/base.py — they operate on other agents' AgentAnalysis
outputs, not on raw ticker/date data.
"""

from dataclasses import dataclass, field
from datetime import date

from agents.base import AgentAnalysis
from config.models import ModelConfig


@dataclass
class VerificationResult:
    analysis: AgentAnalysis
    faithful: bool
    notes: str


class VerifierAgent:
    """Grounds every claim in a citation before it enters debate.

    The original paper only checks RAG faithfulness/relevance for two of its
    three agents (Fundamental, Sentiment) via Arize Phoenix, and never for
    Valuation beyond "did it call the tool." This agent runs the same check
    against every agent's output, uniformly, as a required debate gate
    rather than an offline monitoring pass.
    """

    role = "verifier"

    def __init__(self, model_config: ModelConfig) -> None:
        self.model_config = model_config

    def verify(self, analysis: AgentAnalysis) -> VerificationResult:
        # TODO: for each citation, confirm the excerpt actually appears in
        # (or is faithfully entailed by) the cited source document, and flag
        # any claim in `reasoning` that has no supporting citation at all.
        raise NotImplementedError("citation-grounding check not yet implemented")


class RedTeamAgent:
    """Structurally required to argue against the emerging consensus.

    This is what operationalizes the original paper's unmeasured
    "mitigates cognitive bias" claim: it doesn't just exist as another
    voice, its role prompt forbids agreeing with the majority position
    without first stating the strongest available case against it.
    """

    role = "red_team"

    def __init__(self, model_config: ModelConfig) -> None:
        self.model_config = model_config

    def challenge(
        self, ticker: str, as_of: date, consensus_leaning: AgentAnalysis, supporting: list[AgentAnalysis]
    ) -> AgentAnalysis:
        # TODO: prompt for the strongest case against `consensus_leaning`,
        # grounded in the same data the other agents used (or explicitly
        # flagged as a hypothesis if unsupported by retrieved data).
        raise NotImplementedError("red team challenge not yet implemented")


@dataclass
class DebateRound:
    round_number: int
    analyses: list[AgentAnalysis]
    verifications: list[VerificationResult] = field(default_factory=list)
    red_team_challenge: AgentAnalysis | None = None


@dataclass
class DebateResult:
    ticker: str
    as_of: date
    rounds: list[DebateRound]
    final_recommendation: AgentAnalysis
    converged: bool
    debate_enabled: bool  # False in the single-pass-aggregation ablation

    @property
    def rounds_to_consensus(self) -> int:
        return len(self.rounds)

    @property
    def flipped_from_initial(self) -> bool:
        """Whether the final call differs from round 1's majority-leaning call.

        Logged so the hallucination/debate-value claim is measurable (see
        DESIGN.md) instead of asserted from a single anecdotal transcript.
        """
        if not self.rounds:
            return False
        return self.rounds[0].analyses[0].recommendation != self.final_recommendation.recommendation
