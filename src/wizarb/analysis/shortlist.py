"""Phase 2 candidate shortlist: doc 02 section 4 candidate screening (results, computed).

Ranks (carrier group x UK reporting airport x destination x month) cells by a
gross screening ratio built from CAA base rates, the assumed fare model
(fares/assumptions.py), and an approximate UK261 compensation band
(features/distance_bands.py). This is a *screening* ratio, not the Phase 5 EV
engine: it has no eligibility haircut, no claim friction, no time cost, and no
Eurostat route-volume weighting (that ingest, PLAN.md section 2 item 7, has
not been built). It exists to rank cells for further investigation.

Deferred, not approximated here: GPD tail fits and rotation-index delay
propagation (PLAN.md Phase 2) require flight-level data (Eurocontrol R&D /
OpenSky), which has not been ingested -- Phase 1 only built the CAA aggregate
ingest. Fitting those on CAA's binned percentage data would misrepresent
interval-censored aggregates as flight-level exceedances.
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from wizarb.analysis.base_rates import PANEL, load_arrivals, route_table
from wizarb.config import REPORTS
from wizarb.fares.assumptions import CALIBRATED_CARRIER_GROUPS, assumed_fare
from wizarb.features.distance_bands import SHORT_HAUL_KM, approx_km_from_uk, comp_band_gbp

log = logging.getLogger(__name__)


def _destination_countries(df: pl.DataFrame) -> pl.DataFrame:
    """One country per destination airport name (first observed, CAA spelling is stable)."""
    return (
        df.select(["origin_destination", "origin_destination_country"])
        .drop_nulls()
        .unique(subset=["origin_destination"], keep="first")
    )


def build_shortlist(
    df: pl.DataFrame,
    year: int,
    min_flights: int = 100,
) -> tuple[pl.DataFrame, int]:
    """Rank cells by gross screening ratio = (p_ge_3h * K_gbp) / assumed_fare_gbp.

    Only carrier groups the fare model is actually calibrated for are ranked
    (fares/assumptions.py CALIBRATED_CARRIER_GROUPS) -- other carriers fall
    back to a short/medium-haul "legacy promo fare" default that is not a
    reasonable stand-in for e.g. long-haul network-carrier fares, which would
    make the ranking spurious rather than conservative.

    Returns (ranked table, n_rows_dropped_for_unmapped_country).
    """
    monthly = route_table(df, year, min_flights=min_flights, monthly=True)
    monthly = monthly.filter(pl.col("carrier_group").is_in(CALIBRATED_CARRIER_GROUPS))
    countries = _destination_countries(df)
    joined = monthly.join(countries, on="origin_destination", how="left")

    joined = joined.with_columns(
        pl.col("origin_destination_country")
        .map_elements(approx_km_from_uk, return_dtype=pl.Float64)
        .alias("approx_km")
    )
    n_total = joined.height
    joined = joined.filter(pl.col("approx_km").is_not_null())
    n_dropped = n_total - joined.height

    joined = joined.with_columns(
        pl.col("approx_km").map_elements(comp_band_gbp, return_dtype=pl.Float64).alias("k_gbp"),
        (pl.col("approx_km") > SHORT_HAUL_KM).alias("long_route"),
    )

    fares = [
        assumed_fare(row["carrier_group"], row["month"], long_route=row["long_route"]).fare_gbp
        for row in joined.select(["carrier_group", "month", "long_route"]).iter_rows(named=True)
    ]
    joined = joined.with_columns(pl.Series("assumed_fare_gbp", fares))

    joined = joined.with_columns(
        ((pl.col("p_ge_3h") * pl.col("k_gbp")) / pl.col("assumed_fare_gbp")).alias(
            "gross_screening_ratio"
        )
    )
    ranked = joined.select(
        [
            "carrier_group",
            "reporting_airport",
            "origin_destination",
            "origin_destination_country",
            "month",
            "n_flights",
            "p_ge_3h",
            "p_cancelled",
            "avg_delay_min",
            "approx_km",
            "k_gbp",
            "assumed_fare_gbp",
            "gross_screening_ratio",
        ]
    ).sort(
        ["gross_screening_ratio", "carrier_group", "reporting_airport", "origin_destination", "month"],
        descending=[True, False, False, False, False],
    )
    return ranked, n_dropped


def write_report(panel_path: Path = PANEL, out_dir: Path = REPORTS, top_n: int = 50) -> Path:
    """Write the shortlist CSV + a markdown methodology/results section."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load_arrivals(panel_path)
    year = df.get_column("year").max()
    ranked, n_dropped = build_shortlist(df, year)

    csv_path = out_dir / f"shortlist_{year}.csv"
    ranked.write_csv(csv_path)

    lines = [
        "# Candidate shortlist — computed (doc 02 §4)",
        "",
        f"Year: {year}. Cells: carrier group x UK reporting airport x destination x month, "
        "min 100 arrivals/cell. Full table: `shortlist_{}.csv` ({} rows).".format(
            year, ranked.height
        ),
        "",
        "Restricted to carriers the fare model is calibrated for: "
        + ", ".join(sorted(CALIBRATED_CARRIER_GROUPS))
        + ". Other carriers (network/long-haul) fall back to a short/medium-haul "
        "\"legacy promo fare\" default in the fare model that understates their real fares "
        "and would make the ranking spurious rather than conservative.",
        "",
        "**This is a gross screening ratio, not an EV estimate:**",
        "",
        "```",
        "gross_screening_ratio = (p_ge_3h * K_gbp) / assumed_fare_gbp",
        "```",
        "",
        "- No eligibility haircut (p_e), no collection haircut (p_pi), no claim friction "
        "or time cost (phi) — those are Phase 5 (the EV engine). A ratio > 1 here is *not* "
        "a positive-EV claim.",
        "- `K_gbp` (UK261 220/350/520) is picked from an **approximate** country-centroid "
        "distance table (`features/distance_bands.py`), not measured route distance. "
        f"{n_dropped} cells were dropped (destination country not in the distance table).",
        "- `assumed_fare_gbp` is the Phase-1 fare assumption model, not a measured fare.",
        "- No Eurostat `avia_par_*` route-volume weighting (PLAN.md §2 item 7 not yet "
        "ingested) — thin routes are not down-weighted here.",
        "",
        "**Deferred (not approximated on this data):** GPD tail fits and rotation-index "
        "delay-propagation analysis need flight-level data (Eurocontrol R&D / OpenSky), "
        "which has not been ingested. CAA's percentage-band CSVs are cell-level aggregates; "
        "fitting a peaks-over-threshold tail model on them would treat interval-censored "
        "aggregates as flight-level exceedances, which doc 03 §2.2 flags as invalid.",
        "",
        f"## Top {top_n} cells by gross screening ratio",
        "",
        "| Carrier | UK airport | Destination | Month | n | P(3h+) | K (£) | Fare (£) | ratio |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in ranked.head(top_n).iter_rows(named=True):
        lines.append(
            f"| {r['carrier_group']} | {r['reporting_airport']} | {r['origin_destination']} "
            f"| {r['month']:02d} | {r['n_flights']:,} | {r['p_ge_3h']:.2%} "
            f"| {r['k_gbp']:.0f} | {r['assumed_fare_gbp']:.2f} | {r['gross_screening_ratio']:.2f} |"
        )
    lines.append("")

    out = out_dir / "shortlist.md"
    out.write_text("\n".join(lines))
    log.info("wrote %s and %s", out, csv_path)
    return out
