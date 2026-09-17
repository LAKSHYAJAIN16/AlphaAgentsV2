from datetime import date

import numpy as np
import pytest

from agents.base import AgentAnalysis, Recommendation
from backtest.portfolio import (
    analyses_to_views,
    apply_transaction_costs,
    black_litterman_posterior,
    conviction_to_view_uncertainty,
)


def test_black_litterman_posterior_matches_prior_with_no_views() -> None:
    pi = np.array([0.05, 0.07])
    sigma = np.array([[0.04, 0.01], [0.01, 0.03]])
    # A single view with enormous uncertainty should barely move the prior.
    p = np.array([[1.0, 0.0]])
    q = np.array([0.05])
    omega = np.array([[1e6]])
    posterior = black_litterman_posterior(pi, sigma, p, q, omega)
    assert posterior == pytest.approx(pi, abs=1e-3)


def test_higher_conviction_reduces_view_uncertainty() -> None:
    assert conviction_to_view_uncertainty(10.0) < conviction_to_view_uncertainty(1.0)


def test_analyses_to_views_builds_one_view_per_ticker() -> None:
    analyses = {
        "AAA": AgentAnalysis(
            agent_role="x", ticker="AAA", as_of=date(2026, 1, 1),
            recommendation=Recommendation.BUY, conviction=8.0, reasoning="",
        ),
        "BBB": AgentAnalysis(
            agent_role="x", ticker="BBB", as_of=date(2026, 1, 1),
            recommendation=Recommendation.SELL, conviction=6.0, reasoning="",
        ),
    }
    p, q, omega = analyses_to_views(analyses, tickers=["AAA", "BBB", "CCC"])
    assert p.shape == (2, 3)
    assert q[0] > 0  # BUY -> positive expected return
    assert q[1] < 0  # SELL -> negative expected return
    assert omega.shape == (2, 2)


def test_transaction_costs_reduce_returns_on_turnover() -> None:
    weights = np.array([[1.0, 0.0], [0.0, 1.0]])  # full turnover between periods
    gross = np.array([0.05, 0.05])
    net = apply_transaction_costs(weights, gross, cost_bps=100.0)
    assert np.all(net < gross)
