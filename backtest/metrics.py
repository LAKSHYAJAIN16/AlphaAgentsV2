"""Performance metrics with statistical significance, not single-path plots.

The original paper reports Sharpe ratio and cumulative return as single line
charts with no confidence intervals and no indication of how many times (if
any) the backtest was rerun. Every metric here is designed to be run across
multiple seeds and reported with a bootstrap confidence interval.
"""

import numpy as np


def annualized_sharpe(daily_returns: np.ndarray, risk_free_rate: float, periods_per_year: int = 252) -> float:
    excess = daily_returns - (risk_free_rate / periods_per_year)
    if excess.std(ddof=1) == 0:
        return 0.0
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(periods_per_year))


def bootstrap_sharpe_ci(
    daily_returns: np.ndarray,
    risk_free_rate: float,
    n_bootstrap: int = 2000,
    confidence: float = 0.95,
    periods_per_year: int = 252,
    seed: int | None = None,
) -> tuple[float, float, float]:
    """Block-bootstrap confidence interval on annualized Sharpe.

    Returns (point_estimate, lower, upper). Uses a block bootstrap (not iid
    resampling) because daily returns are autocorrelated — a plain iid
    bootstrap would understate the true variance.
    """
    rng = np.random.default_rng(seed)
    n = len(daily_returns)
    block_size = max(5, n // 20)
    point = annualized_sharpe(daily_returns, risk_free_rate, periods_per_year)

    samples = np.empty(n_bootstrap)
    n_blocks = int(np.ceil(n / block_size))
    for i in range(n_bootstrap):
        starts = rng.integers(0, n - block_size + 1, size=n_blocks)
        resampled = np.concatenate([daily_returns[s : s + block_size] for s in starts])[:n]
        samples[i] = annualized_sharpe(resampled, risk_free_rate, periods_per_year)

    alpha = 1 - confidence
    lower, upper = np.quantile(samples, [alpha / 2, 1 - alpha / 2])
    return point, float(lower), float(upper)


def annualized_volatility(daily_returns: np.ndarray, periods_per_year: int = 252) -> float:
    return float(daily_returns.std(ddof=1) * np.sqrt(periods_per_year))


def cumulative_return(daily_returns: np.ndarray) -> float:
    return float(np.prod(1 + daily_returns) - 1)


def max_drawdown(daily_returns: np.ndarray) -> float:
    cumulative = np.cumprod(1 + daily_returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = cumulative / running_max - 1
    return float(drawdowns.min())
