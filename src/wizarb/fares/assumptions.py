"""Assumed historical fare model.

No free archive of historical *offered* fares exists, so the backtest uses an
explicit, documented fare assumption; a forward-collecting scraper will
eventually replace it for live months (PLAN.md section 2 item 6).

ASSUMPTIONS (not measurements) - sources are directional anchors only:
- Wizz/Ryanair promo fares GBP 15-30 one-way seen on off-peak UK->CEE routes;
  DLR Q1-2025 survey: Wizz average one-way fare ~EUR 67, Ryanair ~EUR 80;
  Ryanair filings: network average fare ~EUR 46-50 (FY2024-25).
- We model the 25th-percentile advance-purchase (3-10 weeks out) one-way fare,
  i.e. deliberately below the network average, since the strategy books cheap
  inventory; a seasonal multiplier captures summer peaking.

The fare model's bias is not neutral: fares and delay propensity are jointly
driven by season/congestion, so any backtest EV is *conditional on this model*
and must be reported as such.
"""

from __future__ import annotations

from dataclasses import dataclass

# Base assumed 25th-pct advance-purchase one-way fare (GBP), by carrier group.
_BASE_FARE_GBP: dict[str, float] = {
    "Wizz Air": 22.0,
    "Ryanair": 18.0,
    "easyJet": 28.0,
    "TUI Airways": 55.0,
    "Jet2.com": 40.0,
}
_DEFAULT_BASE = 45.0  # legacy/network carriers: promo inventory is rare

# Carrier groups the fare model above actually has a calibrated base fare
# for. Everything else falls through to _DEFAULT_BASE, which is a short/
# medium-haul "legacy promo fare" guess -- nowhere near right for long-haul
# network carriers (e.g. an intercontinental BA/Air India economy fare), so
# ranking those cells on assumed_fare would be spurious, not conservative.
CALIBRATED_CARRIER_GROUPS = frozenset(_BASE_FARE_GBP)

# Seasonal multipliers on the base fare (leisure demand peaking).
_SEASON_MULT: dict[int, float] = {
    1: 0.85, 2: 0.85, 3: 0.9, 4: 1.0, 5: 1.05, 6: 1.25,
    7: 1.45, 8: 1.45, 9: 1.1, 10: 1.0, 11: 0.85, 12: 1.1,
}

# Long routes (>1,500 km great-circle -> GBP 350 / EUR 400 band) price higher.
_LONG_ROUTE_UPLIFT = 1.25


@dataclass(frozen=True)
class AssumedFare:
    fare_gbp: float
    basis: str  # provenance string, carried into reports


def assumed_fare(carrier_group: str, month: int, long_route: bool = False) -> AssumedFare:
    """Assumed all-in-ish advance fare. Add ancillaries separately in the EV engine."""
    base = _BASE_FARE_GBP.get(carrier_group, _DEFAULT_BASE)
    fare = base * _SEASON_MULT[month] * (_LONG_ROUTE_UPLIFT if long_route else 1.0)
    return AssumedFare(
        fare_gbp=round(fare, 2),
        basis="assumed 25th-pct advance fare model v0 (see module docstring)",
    )
