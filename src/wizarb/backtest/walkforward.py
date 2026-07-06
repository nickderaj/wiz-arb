"""Phase 6 — walk-forward trading backtest (PLAN.md section 7).

Strategy: at each simulated booking date, rank bookable (carrier x UK airport x
destination x month) cells by the Phase 3 point-in-time predicted rate
(`baseline_pred` — the shrunken cell mean was shown in Phase 3 to be a strong,
near-undominated predictor, so it is the trading signal here, not a re-fit
logistic/GBM); "buy" cells whose predicted EV clears a margin; settle with the
*actual* realized rate for that cell-month (this pipeline's finest available
grain is cell-month, not individual flight — same documented substitution as
Phase 3/5) run through the Phase 4 eligibility/collection haircuts and the
Phase 5 EV engine.

**Because Phase 5 already found EV <= 0 in every (cell x collection x wage)
combination on the most recent cross-section, the baseline trade margin (0)
finds zero trades in every walk-forward year too** — that is the correct,
expected behavior of an honest backtest of a strategy the pipeline has already
shown has no edge, not a bug. To still exercise and report the mechanics this
module implements (cumulative P&L, drawdown, capacity, IRR), a **demonstration
margin** is also run and clearly labeled as such, never as a recommendation.

**Regulatory scenario panel (PLAN.md §7):** the enacted 2026 reform kept the
3h threshold and comp amounts, cutting collection friction via a 30-day
payment deadline — modeled as a shorter DIY payout lag. The Council's
defeated proposal would have raised the threshold; CAA's bands make an exact
4h threshold uncomputable (bands are 121-180 / 181-360 / >360 min, no 240min
cut point), but the >360min (6h) band is exact, so the 6h leg of the
defeated proposal is used as the historical stress case, applied to the
*same* traded cells as a pure settlement counterfactual (not a re-fit
prediction model for a threshold this pipeline never trained one for).
"""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path

import numpy as np
import polars as pl

from wizarb.analysis.base_rates import PANEL, load_arrivals
from wizarb.config import REPORTS
from wizarb.eligibility.haircuts import collection_outcome, p_claimable
from wizarb.ev.engine import EVParams, per_bet_ev
from wizarb.fares.assumptions import CALIBRATED_CARRIER_GROUPS, assumed_fare
from wizarb.features.distance_bands import SHORT_HAUL_KM, approx_km_from_uk, comp_band_gbp
from wizarb.models.features import CELL_KEYS, build_features

log = logging.getLogger(__name__)

SEATS_PER_FLIGHT = 180  # narrowbody LCC assumption, for a capacity order-of-magnitude only
REFORM_DIY_LAG_MONTHS = 1.5  # 30-day statutory deadline + slack (doc 01 §8)
DEMO_TRADE_MARGIN_GBP = -21.0  # relaxed margin used ONLY to demonstrate the harness mechanics
# (chosen empirically to admit a handful of the least-negative-EV cells in this panel --
# the true best predicted EV across 2022-2025 is about -GBP20.2/bet, so this is still a
# deeply negative-EV "trade", never a recommendation, purely a mechanics smoke test)


def _destination_lookup(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.select(["origin_destination", "origin_destination_country"])
        .drop_nulls()
        .unique(subset=["origin_destination"], keep="first")
    )


def build_trading_panel(df: pl.DataFrame) -> pl.DataFrame:
    """Cell-month rows for the calibrated carriers: predicted p_hat, actual 3h/6h rates,
    fare/comp-band economics, and a congestion z-score, all point-in-time correct."""
    feats = build_features(df).filter(pl.col("carrier_group").is_in(CALIBRATED_CARRIER_GROUPS))

    avg_delay = (
        df.group_by(CELL_KEYS + ["year", "month"])
        .agg(
            (pl.col("number_flights_matched") * pl.col("average_delay_mins").fill_null(0)).sum().alias("_wsum"),
            pl.col("number_flights_matched").sum().alias("_n"),
            (
                pl.col("number_flights_matched")
                * pl.col("flights_more_than_360_minutes_late_percent").fill_null(0)
                / 100.0
            ).sum().alias("_n_ge_6h"),
        )
        .with_columns(
            (pl.col("_wsum") / pl.col("_n")).alias("avg_delay_min"),
            (pl.col("_n_ge_6h") / pl.col("_n")).alias("p_ge_6h"),
        )
        .select(CELL_KEYS + ["year", "month", "avg_delay_min", "p_ge_6h"])
    )

    countries = _destination_lookup(df)
    panel = (
        feats.join(avg_delay, on=CELL_KEYS + ["year", "month"], how="left")
        .join(countries, on="origin_destination", how="left")
    )
    panel = panel.with_columns(
        pl.col("origin_destination_country")
        .map_elements(approx_km_from_uk, return_dtype=pl.Float64)
        .alias("approx_km")
    )
    panel = panel.filter(pl.col("approx_km").is_not_null())
    panel = panel.with_columns(
        pl.col("approx_km").map_elements(comp_band_gbp, return_dtype=pl.Float64).alias("k_gbp"),
        (pl.col("approx_km") > SHORT_HAUL_KM).alias("long_route"),
    )
    mean_dd, std_dd = panel.get_column("avg_delay_min").mean(), panel.get_column("avg_delay_min").std()
    panel = panel.with_columns(
        (
            (pl.col("avg_delay_min") - mean_dd) / std_dd if std_dd else pl.lit(0.0)
        ).alias("congestion_z")
    )
    fares = [
        assumed_fare(r["carrier_group"], r["month"], long_route=r["long_route"]).fare_gbp
        for r in panel.select(["carrier_group", "month", "long_route"]).iter_rows(named=True)
    ]
    return panel.with_columns(pl.Series("fare_gbp", fares))


@dataclasses.dataclass
class TradeSettlement:
    year: int
    month: int
    carrier_group: str
    route: str
    n_flights: int
    p_hat: float
    predicted_ev: float
    actual_p_ge_3h: float
    realized_ev_per_bet: float
    realized_ev_total: float
    irr_annualized: float


def _irr(ev_per_bet: float, cost: float, lag_months: float) -> float:
    """Simple single-cashflow IRR: (cost + ev)/cost is the money-multiple at lag_months out."""
    if cost <= 0 or lag_months <= 0:
        return float("nan")
    multiple = (cost + ev_per_bet) / cost
    if multiple <= 0:
        return -1.0
    return multiple ** (12.0 / lag_months) - 1.0


def run_backtest(
    panel: pl.DataFrame,
    first_test_year: int,
    last_test_year: int,
    trade_margin_gbp: float = 0.0,
    collection: str = "diy",
    wage_per_hour: float = 0.0,
    reform: bool = False,
) -> list[TradeSettlement]:
    trades: list[TradeSettlement] = []
    outcome = collection_outcome(collection)
    if reform and collection == "diy":
        outcome = dataclasses.replace(outcome, payout_lag_months=REFORM_DIY_LAG_MONTHS)

    for year in range(first_test_year, last_test_year + 1):
        test = panel.filter(pl.col("year") == year)
        for r in test.iter_rows(named=True):
            claim_pred = p_claimable(r["baseline_pred"], r["month"], r["congestion_z"], collection)
            claim_pred = dataclasses.replace(claim_pred, p_paid=outcome.p_paid, net_multiplier=outcome.net_multiplier)
            ev_pred = per_bet_ev(claim_pred, r["k_gbp"], r["fare_gbp"], EVParams(wage_per_hour=wage_per_hour))
            if ev_pred.ev <= trade_margin_gbp:
                continue

            claim_actual = p_claimable(r["p_ge_3h"], r["month"], r["congestion_z"], collection)
            claim_actual = dataclasses.replace(claim_actual, p_paid=outcome.p_paid, net_multiplier=outcome.net_multiplier)
            ev_actual = per_bet_ev(claim_actual, r["k_gbp"], r["fare_gbp"], EVParams(wage_per_hour=wage_per_hour))

            trades.append(
                TradeSettlement(
                    year=year,
                    month=r["month"],
                    carrier_group=r["carrier_group"],
                    route=f"{r['reporting_airport']}->{r['origin_destination']}",
                    n_flights=int(r["n_flights"]),
                    p_hat=r["baseline_pred"],
                    predicted_ev=ev_pred.ev,
                    actual_p_ge_3h=r["p_ge_3h"],
                    realized_ev_per_bet=ev_actual.ev,
                    realized_ev_total=ev_actual.ev * r["n_flights"],
                    irr_annualized=_irr(ev_actual.ev, ev_actual.all_in_cost, outcome.payout_lag_months),
                )
            )
    return sorted(trades, key=lambda t: (t.year, t.month))


def regulatory_stress(trades: list[TradeSettlement], panel: pl.DataFrame, collection: str = "diy") -> dict:
    """Settle the same traded cells under the defeated 6h-threshold proposal (exact CAA band),
    holding the trade decision fixed -- a pure settlement counterfactual, not a re-fit model."""
    if not trades:
        return {"n_trades": 0, "total_ev_6h": 0.0}
    keys = {(t.year, t.month, t.carrier_group, t.route) for t in trades}
    rows = panel.with_columns((pl.col("reporting_airport") + "->" + pl.col("origin_destination")).alias("route"))
    total = 0.0
    for r in rows.iter_rows(named=True):
        if (r["year"], r["month"], r["carrier_group"], r["route"]) not in keys:
            continue
        claim = p_claimable(r["p_ge_6h"], r["month"], r["congestion_z"], collection)
        ev = per_bet_ev(claim, r["k_gbp"], r["fare_gbp"], EVParams())
        total += ev.ev * r["n_flights"]
    return {"n_trades": len(trades), "total_ev_6h": total}


def _bootstrap_ci(trades: list[TradeSettlement], n_boot: int = 2000, seed: int = 11) -> tuple[float, float]:
    if not trades:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    totals = np.array([t.realized_ev_total for t in trades])
    n = len(totals)
    boots = totals[rng.integers(0, n, size=(n_boot, n))].sum(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(lo), float(hi)


def _summarize(trades: list[TradeSettlement]) -> dict:
    if not trades:
        return {
            "n_trades": 0,
            "total_realized_ev": 0.0,
            "hit_rate": 0.0,
            "max_drawdown": 0.0,
            "capacity_seats": 0,
            "ci_low": 0.0,
            "ci_high": 0.0,
            "mean_irr": float("nan"),
        }
    cum = np.cumsum([t.realized_ev_total for t in trades])
    running_max = np.maximum.accumulate(cum)
    ci_low, ci_high = _bootstrap_ci(trades)
    return {
        "n_trades": len(trades),
        "total_realized_ev": float(cum[-1]),
        "hit_rate": float(np.mean([t.realized_ev_per_bet > 0 for t in trades])),
        "max_drawdown": float((running_max - cum).max()),
        "capacity_seats": int(sum(t.n_flights for t in trades) * SEATS_PER_FLIGHT),
        "ci_low": ci_low,
        "ci_high": ci_high,
        "mean_irr": float(np.nanmean([t.irr_annualized for t in trades])),
    }


def write_report(panel_path: Path = PANEL, out_dir: Path = REPORTS) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load_arrivals(panel_path)
    panel = build_trading_panel(df)
    years = sorted(panel.get_column("year").unique().to_list())
    first_test_year, last_test_year = years[0] + 3, years[-1]

    breakeven_trades = run_backtest(panel, first_test_year, last_test_year, trade_margin_gbp=0.0)
    demo_trades = run_backtest(panel, first_test_year, last_test_year, trade_margin_gbp=DEMO_TRADE_MARGIN_GBP)
    reform_trades = run_backtest(
        panel, first_test_year, last_test_year, trade_margin_gbp=DEMO_TRADE_MARGIN_GBP, reform=True
    )

    be_summary = _summarize(breakeven_trades)
    demo_summary = _summarize(demo_trades)
    reform_summary = _summarize(reform_trades)
    stress = regulatory_stress(demo_trades, panel)

    if demo_trades:
        pl.DataFrame([dataclasses.asdict(t) for t in demo_trades]).write_csv(
            out_dir / "backtest_trades.csv"
        )

    lines = [
        "# Phase 6 — walk-forward trading backtest",
        "",
        f"Walk-forward: trade years {first_test_year}-{last_test_year}, using each cell-month's "
        "point-in-time Phase 3 shrunken-baseline prediction as the trading signal, settled "
        "against the actual realized rate (Phase 4 eligibility + Phase 5 EV engine).",
        "",
        "## Breakeven-threshold backtest (trade iff predicted EV > £0 — the real strategy)",
        "",
        f"- **{be_summary['n_trades']} trades** across {first_test_year}-{last_test_year}.",
        "",
        "This is the expected, correct outcome given Phase 5's cross-sectional result "
        "(EV <= 0 in all 3,474 evaluated combinations): a walk-forward backtest of a "
        "strategy with no measured edge finds no trades. It is not a bug in the harness.",
        "",
        f"## Demonstration backtest (relaxed margin, predicted EV > £{DEMO_TRADE_MARGIN_GBP:.0f} — "
        "mechanics only, NOT a recommended threshold)",
        "",
        f"- Trades: {demo_summary['n_trades']}",
        f"- Total realized EV: £{demo_summary['total_realized_ev']:.2f} "
        f"(95% bootstrap CI [£{demo_summary['ci_low']:.2f}, £{demo_summary['ci_high']:.2f}])",
        f"- Hit rate (bets with positive realized EV): {demo_summary['hit_rate']:.1%}",
        f"- Max drawdown (cumulative realized EV path): £{demo_summary['max_drawdown']:.2f}",
        f"- Capacity: ~{demo_summary['capacity_seats']:,} seats/yr across traded cells "
        f"(assumes {SEATS_PER_FLIGHT} seats/flight — an order-of-magnitude proxy, not measured)",
        f"- Mean annualized IRR per trade: {demo_summary['mean_irr']:.1%}" if demo_trades else "",
        "",
        "## Regulatory scenario panel",
        "",
        "| Scenario | Trades | Total realized EV | Mean IRR |",
        "| --- | ---: | ---: | ---: |",
        f"| Current (pre-reform, 6mo DIY lag) | {demo_summary['n_trades']} "
        f"| £{demo_summary['total_realized_ev']:.2f} | {demo_summary['mean_irr']:.1%} |",
        f"| Post-2026-reform (30-day payment, {REFORM_DIY_LAG_MONTHS}mo DIY lag) "
        f"| {reform_summary['n_trades']} | £{reform_summary['total_realized_ev']:.2f} "
        f"| {reform_summary['mean_irr']:.1%} |",
        f"| Defeated Council proposal (6h exact-band stress, same trades) | {stress['n_trades']} "
        f"| £{stress['total_ev_6h']:.2f} | n/a |",
        "",
        "The reform doesn't change raw EV (it isn't a discount-rate model) — it only "
        "shortens payout latency. For an already-negative-EV trade this makes the "
        "*annualized* IRR look worse, not better: the same sub-1.0 money-multiple gets "
        "raised to a higher power over a shorter period. Faster payment cuts collection "
        "friction, but it does not rescue a trade with no edge. The defeated 6h-threshold "
        "stress case settles the *same* trades against a "
        "much rarer qualifying event and is uniformly worse, as expected — 4h is not "
        "computable from CAA's 121-180/181-360/>360min bands (no 240min cut point), so "
        "only the exact 6h leg of the defeated proposal is shown.",
        "",
    ]

    out = out_dir / "backtest.md"
    out.write_text("\n".join(lines))
    log.info("wrote %s", out)
    return out
