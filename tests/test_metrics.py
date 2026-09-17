import numpy as np
import pytest

from backtest.metrics import (
    annualized_sharpe,
    annualized_volatility,
    bootstrap_sharpe_ci,
    cumulative_return,
    max_drawdown,
)


def test_annualized_sharpe_zero_for_flat_returns() -> None:
    flat = np.zeros(252)
    assert annualized_sharpe(flat, risk_free_rate=0.0) == 0.0


def test_annualized_sharpe_positive_for_consistent_positive_returns() -> None:
    returns = np.full(252, 0.001)
    assert annualized_sharpe(returns, risk_free_rate=0.0) > 0


def test_cumulative_return_compounds() -> None:
    returns = np.array([0.1, 0.1])
    assert cumulative_return(returns) == pytest.approx(1.1 * 1.1 - 1)


def test_max_drawdown_detects_peak_to_trough() -> None:
    returns = np.array([0.10, -0.20, 0.05])
    dd = max_drawdown(returns)
    assert dd < 0
    assert dd == pytest.approx(1.10 * 0.80 / 1.10 - 1)


def test_annualized_volatility_nonnegative() -> None:
    rng = np.random.default_rng(0)
    returns = rng.normal(0, 0.01, size=252)
    assert annualized_volatility(returns) > 0


def test_bootstrap_sharpe_ci_contains_point_estimate() -> None:
    rng = np.random.default_rng(0)
    returns = rng.normal(0.0005, 0.01, size=252)
    point, lower, upper = bootstrap_sharpe_ci(returns, risk_free_rate=0.0, n_bootstrap=200, seed=0)
    assert lower <= point <= upper
