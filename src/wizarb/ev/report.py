"""Phase 5 deliverable: apply the EV engine to the real Phase 2 shortlist.

This is the project's first attempt at the central empirical question: does
any bookable cell clear breakeven once eligibility, collection, ancillary
cost, time cost, and schedule-kill risk are all applied (not just the gross
screening ratio from Phase 2)? Swept across the wage scenarios PLAN.md
names (£0/12/25 per hour) and both collection paths (DIY / agency).
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from wizarb.analysis.base_rates import PANEL, load_arrivals
from wizarb.analysis.shortlist import build_shortlist
from wizarb.config import REPORTS
from wizarb.eligibility.haircuts import p_claimable
from wizarb.ev.engine import (
    WAGE_SCENARIOS_GBP_PER_HOUR,
    EVParams,
    is_band_edge,
    kelly_fraction,
    per_bet_ev,
)
from wizarb.ev.portfolio import simulate_portfolio

log = logging.getLogger(__name__)


def _congestion_z(avg_delay: pl.Series) -> pl.Series:
    mean, std = avg_delay.mean(), avg_delay.std()
    if not std:
        return pl.Series([0.0] * len(avg_delay))
    return (avg_delay - mean) / std


def evaluate_shortlist(ranked: pl.DataFrame) -> pl.DataFrame:
    ranked = ranked.with_columns(
        _congestion_z(ranked.get_column("avg_delay_min")).alias("congestion_z")
    )
    rows = []
    for r in ranked.iter_rows(named=True):
        band_edge = is_band_edge(r["approx_km"])
        for collection in ("diy", "agency"):
            for wage in WAGE_SCENARIOS_GBP_PER_HOUR:
                claim = p_claimable(
                    p_delay=r["p_ge_3h"],
                    month=r["month"],
                    congestion_z=r["congestion_z"],
                    collection=collection,
                )
                ev = per_bet_ev(
                    claim,
                    k_gbp=r["k_gbp"],
                    fare_gbp=r["assumed_fare_gbp"],
                    params=EVParams(wage_per_hour=wage),
                )
                k_net = r["k_gbp"] * claim.net_multiplier
                rows.append(
                    {
                        "carrier_group": r["carrier_group"],
                        "reporting_airport": r["reporting_airport"],
                        "origin_destination": r["origin_destination"],
                        "month": r["month"],
                        "n_flights": r["n_flights"],
                        "p_ge_3h": r["p_ge_3h"],
                        "band_edge": band_edge,
                        "collection": collection,
                        "wage_per_hour": wage,
                        "p_eligible": claim.p_eligible,
                        "p_claimable": claim.p_claimable,
                        "k_gbp": r["k_gbp"],
                        "fare_gbp": r["assumed_fare_gbp"],
                        "k_net_gbp": k_net,
                        "all_in_cost_gbp": ev.all_in_cost,
                        "ev_gbp": ev.ev,
                        "breakeven_p_claimable": ev.breakeven_p_claimable,
                        "kelly_f": kelly_fraction(claim.p_claimable, k_net, ev.all_in_cost),
                    }
                )
    return pl.DataFrame(rows).sort("ev_gbp", descending=True)


def write_report(panel_path: Path = PANEL, out_dir: Path = REPORTS, top_n: int = 25) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load_arrivals(panel_path)
    year = df.get_column("year").max()
    ranked, _ = build_shortlist(df, year)
    evaluated = evaluate_shortlist(ranked)
    evaluated.write_csv(out_dir / "ev_ranked.csv")

    best = evaluated.row(0, named=True)
    any_positive = evaluated.filter(pl.col("ev_gbp") > 0)

    portfolio = simulate_portfolio(
        p_delay=best["p_ge_3h"],
        month=best["month"],
        k_gbp=best["k_gbp"],
        fare_gbp=best["fare_gbp"],
        collection=best["collection"],
        ev_params=EVParams(wage_per_hour=best["wage_per_hour"]),
    )

    lines = [
        "# Phase 5 — EV engine applied to the Phase 2 shortlist",
        "",
        f"Year {year}. {evaluated.height:,} (cell x collection-path x wage-scenario) combinations "
        f"evaluated from {ranked.height:,} shortlisted cells. Full table: `ev_ranked.csv`.",
        "",
        "**Central result:** "
        + (
            f"**{any_positive.height:,} combinations clear breakeven (EV > 0).**"
            if any_positive.height
            else "**no (cell x collection x wage) combination clears breakeven — EV ≤ 0 everywhere evaluated.**"
        ),
        "",
        "## Best combination found",
        "",
        f"- {best['carrier_group']} {best['reporting_airport']}→{best['origin_destination']}, "
        f"month {best['month']:02d}",
        f"- P(3h+) = {best['p_ge_3h']:.2%}, p_eligible = {best['p_eligible']:.1%}, "
        f"p_claimable = {best['p_claimable']:.3%}",
        f"- Collection: {best['collection']}, wage £{best['wage_per_hour']:.0f}/h",
        f"- K_net = £{best['k_net_gbp']:.0f}, all-in cost = £{best['all_in_cost_gbp']:.2f}",
        f"- **EV = £{best['ev_gbp']:.2f}** per bet "
        f"(breakeven p_claimable = {best['breakeven_p_claimable']:.3%})",
        f"- Kelly fraction f = {best['kelly_f']:.4f}",
        "",
        "## Monte Carlo portfolio (best combination, 250 bets, 2000 sims)",
        "",
        f"- Mean season P&L: £{portfolio.mean_pnl:.2f} (std £{portfolio.std_pnl:.2f}, "
        f"Sharpe {portfolio.sharpe:.3f})",
        f"- 95% CI: [£{portfolio.ci_low:.2f}, £{portfolio.ci_high:.2f}]",
        f"- Mean max drawdown: £{portfolio.mean_max_drawdown:.2f}",
        f"- Hit rate (bets that actually pay out): {portfolio.hit_rate:.3%}",
        f"- Same-day clustering: gross delay correlation {portfolio.gross_delay_corr:.3f} vs. "
        f"eligibility-filtered (claimable) correlation {portfolio.claimable_corr:.3f} — "
        "independent per-flight eligibility draws attenuate the clustered tail, as doc 04 §7 argues.",
        "",
        f"## Top {top_n} combinations by EV",
        "",
        "| Carrier | Route | Month | Collection | Wage £/h | P(3h+) | p_claimable | K_net £ | "
        "Cost £ | EV £ | Kelly f |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in evaluated.head(top_n).iter_rows(named=True):
        lines.append(
            f"| {r['carrier_group']} | {r['reporting_airport']}→{r['origin_destination']} "
            f"| {r['month']:02d} | {r['collection']} | {r['wage_per_hour']:.0f} "
            f"| {r['p_ge_3h']:.2%} | {r['p_claimable']:.3%} | {r['k_net_gbp']:.0f} "
            f"| {r['all_in_cost_gbp']:.2f} | {r['ev_gbp']:.2f} | {r['kelly_f']:.4f} |"
        )
    lines += [
        "",
        "**Not priced (see `ev/engine.py` docstring):** missed-connection uplift, cancellation/"
        "re-routing legs, duty-of-care in-kind value — all require single-booking itinerary or "
        "per-flight cause data this pipeline never ingested. Only the pure-function band-edge "
        f"screen ({(evaluated.filter(pl.col('band_edge')).height):,} of {evaluated.height:,} rows "
        "flagged within 150km of a compensation breakpoint) is included.",
        "",
    ]

    out = out_dir / "ev.md"
    out.write_text("\n".join(lines))
    log.info("wrote %s", out)
    return out
