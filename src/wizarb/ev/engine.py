"""Phase 5 — per-bet EV, breakeven, and Kelly sizing (PLAN.md section 6).

    EV = p_claimable * K_net - c - phi

`c` is the **all-in** cost (headline fare + bag/seat/card ancillaries — doc 04's
€10-20 estimate); `phi` is the parameterized time cost (doc 04 §1.2: 4-10h/bet,
reported at wage 0 / 12 / 25 per hour, currency-matched to the UK261 GBP bands
this pipeline actually computed a shortlist in). A **schedule-change kill
probability** (doc 04 §7: ~3-10% of months-ahead bookings lose the selected
rotation to a re-timing/refund) is applied multiplicatively: a killed booking
is refunded, so it contributes zero cost and zero payout, not a loss.

**Secondary payoff legs named in PLAN.md §6** (missed-connection uplift under
_Folkerts_, band-edge screening, cancellation/re-routing legs, duty-of-care
value) are **not priced here.** All of them require single-booking itinerary
or per-flight cause data this pipeline never ingested (CAA's cell aggregates
have no PNR/itinerary concept); pricing them from an assumption alone would
manufacture the "one channel that could move the geometry" (PLAN.md §8)
without evidence, which is worse than leaving it an open, flagged gap. Only
the 1,500km band-edge screen is a pure function of an already-modeled
quantity (approx_km) and is included.
"""

from __future__ import annotations

from dataclasses import dataclass

from wizarb.eligibility.haircuts import ClaimableResult
from wizarb.features.distance_bands import LONG_HAUL_KM, SHORT_HAUL_KM

DEFAULT_ANCILLARY_GBP = 15.0
DEFAULT_HOURS_PER_BET = 7.0  # midpoint of doc 04's 4-10h range
DEFAULT_SCHEDULE_KILL_PROB = 0.05  # midpoint of doc 04's 3-10% range
WAGE_SCENARIOS_GBP_PER_HOUR = (0.0, 12.0, 25.0)
BAND_EDGE_BUFFER_KM = 150.0


@dataclass(frozen=True)
class EVParams:
    wage_per_hour: float = 0.0
    hours_per_bet: float = DEFAULT_HOURS_PER_BET
    ancillary_gbp: float = DEFAULT_ANCILLARY_GBP
    schedule_kill_prob: float = DEFAULT_SCHEDULE_KILL_PROB


@dataclass(frozen=True)
class EVResult:
    all_in_cost: float
    time_cost: float
    gross_payout: float  # p_claimable * K_net, before cost/time/kill
    ev_if_completed: float  # gross_payout - all_in_cost - time_cost
    ev: float  # ev_if_completed * (1 - schedule_kill_prob)
    breakeven_p_claimable: float  # p_claimable that zeroes ev_if_completed, at this K_net/cost/phi


def per_bet_ev(
    claim: ClaimableResult,
    k_gbp: float,
    fare_gbp: float,
    params: EVParams = EVParams(),
) -> EVResult:
    k_net = k_gbp * claim.net_multiplier
    all_in_cost = fare_gbp + params.ancillary_gbp
    time_cost = params.wage_per_hour * params.hours_per_bet
    gross_payout = claim.p_claimable * k_net
    ev_completed = gross_payout - all_in_cost - time_cost
    ev = ev_completed * (1 - params.schedule_kill_prob)
    breakeven_p = (all_in_cost + time_cost) / k_net if k_net > 0 else float("inf")
    return EVResult(
        all_in_cost=all_in_cost,
        time_cost=time_cost,
        gross_payout=gross_payout,
        ev_if_completed=ev_completed,
        ev=ev,
        breakeven_p_claimable=breakeven_p,
    )


def kelly_fraction(p: float, k_net: float, c: float) -> float:
    """f = (pK - c)/(K - c) (PLAN.md section 6). Clipped to [0, 1]: never bet on a
    negative-edge outcome, never leverage beyond bankroll in this simple single-outcome
    formulation (no reinvestment of unclaimed receivables modeled)."""
    if k_net <= c:
        return 0.0
    f = (p * k_net - c) / (k_net - c)
    return min(max(f, 0.0), 1.0)


def is_band_edge(km: float | None, buffer_km: float = BAND_EDGE_BUFFER_KM) -> bool:
    """True if a route sits within `buffer_km` of a compensation breakpoint (1,500/3,500km) —
    doc 03 §1.4's band-edge screen: routes just over the boundary pay the higher band at a
    fare similar to routes just under it."""
    if km is None:
        return False
    return any(abs(km - edge) <= buffer_km for edge in (SHORT_HAUL_KM, LONG_HAUL_KM))
