"""Phase 5 — Monte Carlo portfolio simulation with bootstrap CIs (PLAN.md section 6).

Delay risk is not independent across flights: mass-delay days cluster (ATC,
weather), but the clustered tail is mostly exempt (doc 04 §7). We model this
with a shared per-day multiplicative shock on the *delay* probability (creates
gross correlation) while the eligibility draw (non-extraordinary cause) stays
independent per flight (idiosyncratic causes don't cluster the same way) —
this is a stylized mechanism to *demonstrate* the attenuation qualitatively,
not a fitted correlation structure (no cause-code panel exists to fit one
from; PLAN.md Phase 1 item 2/4 not ingested).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from wizarb.eligibility.haircuts import collection_outcome, eligibility_share
from wizarb.ev.engine import EVParams


@dataclass(frozen=True)
class PortfolioResult:
    n_bets: int
    n_sims: int
    mean_pnl: float
    std_pnl: float
    sharpe: float
    ci_low: float
    ci_high: float
    mean_max_drawdown: float
    hit_rate: float
    gross_delay_corr: float  # same-day vs cross-day correlation of raw delay indicator
    claimable_corr: float  # same-day vs cross-day correlation of the paid-out indicator


def simulate_portfolio(
    p_delay: float,
    month: int,
    k_gbp: float,
    fare_gbp: float,
    collection: str = "diy",
    ev_params: EVParams = EVParams(),
    n_bets: int = 250,
    bets_per_day: int = 2,
    day_shock_sigma: float = 0.6,
    n_sims: int = 2000,
    seed: int = 7,
) -> PortfolioResult:
    rng = np.random.default_rng(seed)
    n_days = int(np.ceil(n_bets / bets_per_day))
    p_eligible = eligibility_share(month)
    outcome = collection_outcome(collection)
    k_net = k_gbp * outcome.net_multiplier
    all_in_cost = fare_gbp + ev_params.ancillary_gbp
    time_cost = ev_params.wage_per_hour * ev_params.hours_per_bet

    pnl_paths = np.zeros((n_sims, n_bets))
    delay_flat = np.zeros((n_sims, n_bets), dtype=bool)
    claim_flat = np.zeros((n_sims, n_bets), dtype=bool)
    day_of_bet = np.repeat(np.arange(n_days), bets_per_day)[:n_bets]

    for s in range(n_sims):
        day_shock = rng.normal(0.0, day_shock_sigma, size=n_days)
        p_delay_bet = np.clip(p_delay * np.exp(day_shock[day_of_bet]), 0.0, 1.0)

        delayed = rng.random(n_bets) < p_delay_bet
        eligible = rng.random(n_bets) < p_eligible  # idiosyncratic, independent per bet
        paid = rng.random(n_bets) < outcome.p_paid
        killed = rng.random(n_bets) < ev_params.schedule_kill_prob

        claimable = delayed & eligible & paid & ~killed
        payout = np.where(claimable, k_net, 0.0)
        cost = np.where(killed, 0.0, all_in_cost + time_cost)
        pnl_paths[s] = payout - cost

        delay_flat[s] = delayed
        claim_flat[s] = claimable

    totals = pnl_paths.sum(axis=1)
    cum = np.cumsum(pnl_paths, axis=1)
    running_max = np.maximum.accumulate(cum, axis=1)
    drawdowns = (running_max - cum).max(axis=1)

    ci_low, ci_high = np.percentile(totals, [2.5, 97.5])

    def _same_vs_cross_day_corr(flat: np.ndarray) -> float:
        """Corr(outcome_i, outcome_j) for same-day pairs minus cross-day pairs, averaged
        over sims — a simple clustering diagnostic, not a full covariance estimate."""
        same_day_stats = []
        for d in range(min(n_days, 40)):  # cap for runtime; a diagnostic, not exhaustive
            idx = np.where(day_of_bet == d)[0]
            if len(idx) < 2:
                continue
            pair = flat[:, idx].astype(float)
            if pair[:, 0].std() == 0 or pair[:, 1].std() == 0:
                continue
            corr = np.corrcoef(pair[:, 0], pair[:, 1])[0, 1]
            if not np.isnan(corr):
                same_day_stats.append(corr)
        return float(np.mean(same_day_stats)) if same_day_stats else 0.0

    return PortfolioResult(
        n_bets=n_bets,
        n_sims=n_sims,
        mean_pnl=float(totals.mean()),
        std_pnl=float(totals.std()),
        sharpe=float(totals.mean() / totals.std()) if totals.std() > 0 else 0.0,
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        mean_max_drawdown=float(drawdowns.mean()),
        hit_rate=float(claim_flat.mean()),
        gross_delay_corr=_same_vs_cross_day_corr(delay_flat),
        claimable_corr=_same_vs_cross_day_corr(claim_flat),
    )
