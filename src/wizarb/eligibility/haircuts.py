"""Phase 4 — eligibility and collection haircuts (PLAN.md section 5).

    p_claimable = p_delay * p_eligible(non-extraordinary | delay) * p_paid(valid claim)

**Flagged as unvalidated (PLAN.md §5, doc 04 risk register):** no published statistic
gives the compensable share of 3h+ delays by cell — this is the headline sensitivity
axis of the whole project. Every number in this module is a documented assumption
anchored to doc 01/04's cited sources (CODA cause shares, AirHelp rejection-rate data,
CAA enforcement reports), not a fitted parameter. The EV engine (Phase 5) must sweep
these, not treat them as constants.

Structural facts these assumptions encode (doc 01 §4.3, doc 04 §7):
- Correlated mass-delay days (ATC, strikes, ATFM regulation) are mostly *exempt* as
  "extraordinary circumstances" — the tail you'd want to bet on pays close to €0.
- Weather is an affirmative defence, not a blanket exemption: ordinary weather/de-icing
  and reactionary knock-on delays are contestable (German BGH X ZR 146/23; the C-74/19
  causal-link/reasonable-measures limbs). ~20-40% of weather-tagged 3h+ delays are
  plausibly compensable.
- Technical/crew causes (airline-internal, *Wallentin-Hermann*) are compensable absent
  a hidden manufacturing defect defence, which airlines raise but rarely sustain.
- The cause mix is seasonal: winter skews weather/de-icing, summer skews ATC/ATFM
  capacity regulation (doc 01 §4.3, doc 04 §7).
"""

from __future__ import annotations

from dataclasses import dataclass

WINTER_MONTHS = {12, 1, 2}
SUMMER_MONTHS = {6, 7, 8}

# Cause-bucket shares of all 3h+ delays, by season. Anchored to EUROCONTROL CODA
# network-level cause shares (ATFM/weather/reactionary/other) as directional priors,
# not a fitted per-cell decomposition -- CODA data has not been ingested (PLAN.md
# Phase 1 item 2). Rows sum to 1.0.
CAUSE_MIX: dict[str, dict[str, float]] = {
    "winter": {"technical_crew": 0.30, "weather": 0.40, "atc_atfm": 0.20, "other": 0.10},
    "summer": {"technical_crew": 0.30, "weather": 0.15, "atc_atfm": 0.45, "other": 0.10},
    "shoulder": {"technical_crew": 0.35, "weather": 0.25, "atc_atfm": 0.30, "other": 0.10},
}

# Within-bucket compensable share (doc 01 §4.3 / doc 04 §4,7).
COMPENSABLE_SHARE: dict[str, float] = {
    "technical_crew": 0.85,  # Wallentin-Hermann; airline rarely sustains a hidden-defect defence
    "weather": 0.30,  # midpoint of the 20-40% contestable range
    "atc_atfm": 0.08,  # strikes/ATFM regulation are the paradigm exempt cause; own-staff-strike carve-out is rare
    "other": 0.45,  # unresolved cause bucket: treated as a coin-flip-ish midpoint, not measured
}

# Congestion sensitivity: cells with materially worse average delay skew further
# toward correlated (ATC/weather) causation, so eligibility share should *decrease*
# with congestion, not stay flat. `congestion_z` is a z-score of avg delay minutes
# across cells (caller-supplied, e.g. from analysis.base_rates); 0.0 = average cell.
_CONGESTION_SLOPE = -0.03  # p_eligible per unit of z; keeps the swing modest and bounded below
_P_ELIGIBLE_MIN = 0.20
_P_ELIGIBLE_MAX = 0.60


def _season(month: int) -> str:
    if month in WINTER_MONTHS:
        return "winter"
    if month in SUMMER_MONTHS:
        return "summer"
    return "shoulder"


def cause_mix(month: int) -> dict[str, float]:
    """Assumed seasonal cause-bucket shares of 3h+ delays (doc 01 §4.3)."""
    return dict(CAUSE_MIX[_season(month)])


def eligibility_share(month: int, congestion_z: float = 0.0) -> float:
    """p(non-extraordinary | delay) for a cell-month: weighted cause mix x compensable share,
    adjusted for congestion (worse cells skew toward exempt correlated causes).
    """
    mix = cause_mix(month)
    base = sum(mix[cause] * COMPENSABLE_SHARE[cause] for cause in mix)
    adjusted = base + _CONGESTION_SLOPE * congestion_z
    return min(max(adjusted, _P_ELIGIBLE_MIN), _P_ELIGIBLE_MAX)


@dataclass(frozen=True)
class CollectionOutcome:
    p_paid: float  # p(paid | valid, non-extraordinary claim)
    net_multiplier: float  # fraction of gross compensation actually received (fees)
    payout_lag_months: float  # expected time-to-cash, for IRR/latency treatment
    basis: str


# Collection paths (doc 04 §3, §7): ~52% of valid claims rejected on first contact
# (AirHelp 2024 UK data); persistence through ADR/court eventually recovers most
# valid claims DIY, slower; agencies recover faster and more reliably for a
# 25-50% contingency cut.
_COLLECTION: dict[str, CollectionOutcome] = {
    "diy": CollectionOutcome(
        p_paid=0.80,
        net_multiplier=1.0,
        payout_lag_months=6.0,
        basis="DIY persistence through ADR/court; ~80% eventual success, 2-12mo (doc 04 §7)",
    ),
    "agency": CollectionOutcome(
        p_paid=0.90,
        net_multiplier=0.65,  # midpoint of 25-50% contingency cut
        payout_lag_months=3.0,
        basis="claims agency (e.g. AirHelp/Skycop-style); faster + higher hit rate, 35% cut",
    ),
}


def collection_outcome(path: str = "diy") -> CollectionOutcome:
    if path not in _COLLECTION:
        raise ValueError(f"unknown collection path {path!r}; choose from {list(_COLLECTION)}")
    return _COLLECTION[path]


@dataclass(frozen=True)
class ClaimableResult:
    p_delay: float
    p_eligible: float
    p_paid: float
    p_claimable: float
    net_multiplier: float
    payout_lag_months: float


def p_claimable(
    p_delay: float,
    month: int,
    congestion_z: float = 0.0,
    collection: str = "diy",
) -> ClaimableResult:
    """p_claimable = p_delay * p_eligible * p_paid, plus the net-payout and latency
    haircuts the EV engine needs (net_multiplier, payout_lag_months)."""
    p_e = eligibility_share(month, congestion_z)
    outcome = collection_outcome(collection)
    p_c = p_delay * p_e * outcome.p_paid
    return ClaimableResult(
        p_delay=p_delay,
        p_eligible=p_e,
        p_paid=outcome.p_paid,
        p_claimable=p_c,
        net_multiplier=outcome.net_multiplier,
        payout_lag_months=outcome.payout_lag_months,
    )
