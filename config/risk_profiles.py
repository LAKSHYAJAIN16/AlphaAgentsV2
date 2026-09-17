"""Risk-tolerance profiles.

The original paper conditions agents on risk tolerance with a single
adjective in the role prompt ("risk-averse", "risk-neutral", "risk-seeking").
Risk-seeking came out statistically indistinguishable from risk-neutral and
was quietly dropped rather than investigated. Giving each profile concrete
numeric anchors — not just an adjective — is the fix: the agent reasons
against a defined threshold instead of inferring behavioral difference from
a word.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskProfile:
    name: str
    # Max annualized volatility the agent should accept in a BUY call.
    max_accepted_volatility: float
    # Minimum conviction (0-10) required before a BUY is issued.
    min_conviction_to_buy: float
    # How much weight momentum/short-term signals get vs. fundamentals,
    # 0 = pure fundamentals, 1 = pure momentum.
    momentum_weight: float
    description: str


RISK_AVERSE = RiskProfile(
    name="risk_averse",
    max_accepted_volatility=0.25,
    min_conviction_to_buy=7.0,
    momentum_weight=0.15,
    description=(
        "Accept volatility up to 25% annualized. Require strong conviction "
        "(>=7/10) before recommending BUY. Weight fundamentals heavily over "
        "momentum (85/15)."
    ),
)

RISK_NEUTRAL = RiskProfile(
    name="risk_neutral",
    max_accepted_volatility=0.45,
    min_conviction_to_buy=5.0,
    momentum_weight=0.40,
    description=(
        "Accept volatility up to 45% annualized. Moderate conviction "
        "threshold (>=5/10). Balance fundamentals and momentum (60/40)."
    ),
)

RISK_SEEKING = RiskProfile(
    name="risk_seeking",
    max_accepted_volatility=0.80,
    min_conviction_to_buy=3.5,
    momentum_weight=0.65,
    description=(
        "Accept volatility up to 80% annualized. Lower conviction threshold "
        "(>=3.5/10) — willing to act on early/uncertain signals. Weight "
        "momentum over fundamentals (35/65), explicitly favoring names with "
        "recent strong price action even without full fundamental support."
    ),
)

ALL_PROFILES = {p.name: p for p in (RISK_AVERSE, RISK_NEUTRAL, RISK_SEEKING)}
