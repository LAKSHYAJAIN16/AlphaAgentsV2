from datetime import date

import pytest

from agents.base import AgentAnalysis, Recommendation


def _make_analysis(conviction: float) -> AgentAnalysis:
    return AgentAnalysis(
        agent_role="test",
        ticker="TEST",
        as_of=date(2026, 1, 1),
        recommendation=Recommendation.BUY,
        conviction=conviction,
        reasoning="test",
    )


def test_conviction_in_range_accepted() -> None:
    assert _make_analysis(0.0).conviction == 0.0
    assert _make_analysis(10.0).conviction == 10.0


@pytest.mark.parametrize("bad_conviction", [-0.1, 10.1, 100])
def test_conviction_out_of_range_rejected(bad_conviction: float) -> None:
    with pytest.raises(ValueError):
        _make_analysis(bad_conviction)
