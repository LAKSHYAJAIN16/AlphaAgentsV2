"""Backtest universe and time-window definitions.

Fixes two of the original paper's evaluation gaps directly:
- 15 tech-only names -> stratified multi-sector universe
- one 4-month bull-market window -> multiple disjoint regimes
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class BacktestWindow:
    name: str
    start: date
    end: date
    regime_note: str


# Placeholder windows spanning distinct regimes. Exact dates/tickers to be
# finalized against data availability and each model's training cutoff (a
# window must fall entirely after the evaluated model's cutoff to avoid the
# look-ahead/memorization confound described in DESIGN.md).
BACKTEST_WINDOWS = [
    BacktestWindow(
        name="2022_bear",
        start=date(2022, 1, 1),
        end=date(2022, 10, 1),
        regime_note="Rate-hike-driven drawdown across growth/tech",
    ),
    BacktestWindow(
        name="2023_recovery",
        start=date(2023, 1, 1),
        end=date(2023, 12, 31),
        regime_note="Broad recovery, early AI-driven tech leadership",
    ),
    BacktestWindow(
        name="post_cutoff_holdout",
        start=date(2026, 2, 1),
        end=date(2026, 8, 1),
        regime_note=(
            "Entirely after model training cutoff — primary window for "
            "testing genuine prediction vs. memorization"
        ),
    ),
]

# Sector buckets to stratify the universe by, rather than sampling one
# sector as the original paper did.
SECTOR_BUCKETS = [
    "technology",
    "healthcare",
    "financials",
    "energy",
    "consumer_staples",
    "industrials",
]
