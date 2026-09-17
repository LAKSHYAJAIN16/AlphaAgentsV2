"""Multi-agent debate orchestration.

The `debate_enabled` flag exists specifically to make the debate-value
ablation possible (DESIGN.md): the same agents, same data, same day, run
once with `debate_enabled=True` (full round-robin until consensus or
max_rounds) and once with `debate_enabled=False` (single pass, analyses
aggregated without cross-agent discussion). Comparing the two is the direct
test of the original paper's unmeasured "debate reduces hallucination"
claim.
"""

from datetime import date

from agents.base import Agent, AgentAnalysis, Recommendation
from debate.protocol import DebateResult, DebateRound, RedTeamAgent, VerifierAgent


class DebateOrchestrator:
    def __init__(
        self,
        analysts: list[Agent],
        verifier: VerifierAgent,
        red_team: RedTeamAgent,
        max_rounds: int = 4,
    ) -> None:
        self.analysts = analysts
        self.verifier = verifier
        self.red_team = red_team
        self.max_rounds = max_rounds

    def run(self, ticker: str, as_of: date, debate_enabled: bool = True) -> DebateResult:
        rounds: list[DebateRound] = []

        round_1_analyses = [a.analyze(ticker, as_of) for a in self.analysts]
        round_1_verifications = [self.verifier.verify(a) for a in round_1_analyses]
        rounds.append(DebateRound(round_number=1, analyses=round_1_analyses, verifications=round_1_verifications))

        if not debate_enabled:
            final = self._aggregate(round_1_analyses)
            return DebateResult(
                ticker=ticker,
                as_of=as_of,
                rounds=rounds,
                final_recommendation=final,
                converged=True,
                debate_enabled=False,
            )

        # TODO: round-robin re-prompting each analyst with peers' prior-round
        # analyses attached, re-verify, invoke red_team.challenge against the
        # emerging majority leaning, and loop until consensus (all
        # recommendations agree) or self.max_rounds is reached.
        raise NotImplementedError("debate round-robin loop not yet implemented")

    def _aggregate(self, analyses: list[AgentAnalysis]) -> AgentAnalysis:
        """Conviction-weighted majority vote, used only in the no-debate ablation."""
        votes: dict[Recommendation, float] = {}
        for a in analyses:
            votes[a.recommendation] = votes.get(a.recommendation, 0.0) + a.conviction
        winner = max(votes, key=votes.get)
        winning_analyses = [a for a in analyses if a.recommendation == winner]
        avg_conviction = sum(a.conviction for a in winning_analyses) / len(winning_analyses)
        return AgentAnalysis(
            agent_role="aggregate_no_debate",
            ticker=analyses[0].ticker,
            as_of=analyses[0].as_of,
            recommendation=winner,
            conviction=avg_conviction,
            reasoning="Conviction-weighted vote across agents, no debate (ablation control).",
        )
