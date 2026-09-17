"""Position sizing via Black-Litterman, and transaction-cost accounting.

The original paper only ever produces equal-weighted binary BUY/SELL
baskets and explicitly names weighting-by-confidence as future work it
didn't do. This implements that: agent conviction scores become
Black-Litterman "views" combined with a market-equilibrium prior, rather
than a naive convert-conviction-directly-to-weight heuristic.
"""

import numpy as np

from agents.base import AgentAnalysis, Recommendation


def black_litterman_posterior(
    pi: np.ndarray,
    sigma: np.ndarray,
    p: np.ndarray,
    q: np.ndarray,
    omega: np.ndarray,
    tau: float = 0.05,
) -> np.ndarray:
    """Posterior expected returns.

    pi: (n,) market-equilibrium implied returns
    sigma: (n, n) covariance matrix
    p: (k, n) view matrix (one row per view, one column per asset)
    q: (k,) view expected returns
    omega: (k, k) view uncertainty (diagonal — views assumed independent)
    """
    tau_sigma_inv = np.linalg.inv(tau * sigma)
    omega_inv = np.linalg.inv(omega)

    posterior_cov_inv = tau_sigma_inv + p.T @ omega_inv @ p
    posterior_cov = np.linalg.inv(posterior_cov_inv)
    posterior_mean = posterior_cov @ (tau_sigma_inv @ pi + p.T @ omega_inv @ q)
    return posterior_mean


def conviction_to_view_uncertainty(conviction: float, base_variance: float = 0.05) -> float:
    """Higher conviction -> lower view variance (more weight in the posterior).

    conviction in [0, 10]. Maps conviction=10 to base_variance, conviction=0
    to 10x base_variance, so a low-conviction call barely moves the prior
    and a high-conviction call can move it substantially — this is the
    mechanism that replaces the original paper's binary equal-weight
    inclusion/exclusion.
    """
    scale = 10.0 - min(max(conviction, 0.0), 10.0)
    return base_variance * (1.0 + scale)


def analyses_to_views(
    analyses_by_ticker: dict[str, AgentAnalysis], tickers: list[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build absolute per-asset views (P, Q, Omega) from final debate outputs.

    Each ticker with a final analysis becomes one absolute view: an assumed
    expected excess return magnitude in the direction of the recommendation,
    scaled by conviction. The magnitude mapping (5% for BUY, -5% for SELL)
    is a placeholder pending calibration against realized returns.
    """
    view_tickers = [t for t in tickers if t in analyses_by_ticker]
    n_assets = len(tickers)
    k_views = len(view_tickers)

    p = np.zeros((k_views, n_assets))
    q = np.zeros(k_views)
    omega_diag = np.zeros(k_views)

    for i, ticker in enumerate(view_tickers):
        analysis = analyses_by_ticker[ticker]
        j = tickers.index(ticker)
        p[i, j] = 1.0
        direction = 1.0 if analysis.recommendation == Recommendation.BUY else -1.0
        q[i] = direction * 0.05 * (analysis.conviction / 10.0)
        omega_diag[i] = conviction_to_view_uncertainty(analysis.conviction)

    return p, q, np.diag(omega_diag)


def apply_transaction_costs(
    weights_over_time: np.ndarray, gross_returns: np.ndarray, cost_bps: float = 10.0
) -> np.ndarray:
    """Deduct turnover-proportional transaction costs from gross returns.

    weights_over_time: (T, n) portfolio weights at each rebalance
    gross_returns: (T,) gross portfolio return each period, before costs
    cost_bps: one-way transaction cost in basis points per unit turnover

    Absent from the original paper entirely — it reports gross returns only.
    """
    turnover = np.sum(np.abs(np.diff(weights_over_time, axis=0)), axis=1)
    turnover = np.concatenate([[np.sum(np.abs(weights_over_time[0]))], turnover])
    cost = turnover * (cost_bps / 10_000.0)
    return gross_returns - cost
