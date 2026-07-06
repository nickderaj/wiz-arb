"""Phase 3 feature engineering on the CAA cell panel.

**Data-reality adaptation (documented, not silent):** PLAN.md Phase 3 frames the
target as a per-*flight* binary `delay_arrival >= 180 min`. CAA's public CSVs are
not flight-level: each row is already a (reporting airport x destination x
airline x scheduled/charter x month) *cell* with a matched-flight count and a
delay-band percentage. There is no flight-level record to bind a booking-time
feature vector to in this data source (that requires Eurocontrol R&D / OpenSky,
PLAN.md Phase 1 items 3-4, not ingested). We therefore model the **cell-month
delay rate** as a binomial outcome (`n_ge_3h` successes out of `n_flights`
trials) and evaluate with rate-weighted Brier/log-loss rather than per-flight
metrics. This is the finest grain the ingested data supports; it is a
deliberate substitution, not an approximation of something we could measure
better.

**Point-in-time discipline:** CAA publishes ~2-3 months in arrears (PLAN.md
section 2). A simulated booking made ~28 days before a flight in month M can
only see CAA data up to roughly month M-4. All trailing features here are
computed with a `lag_months` gap before `window_months` of history, so no
feature for a test-year row ever touches same-period or future data.
"""

from __future__ import annotations

import polars as pl

from wizarb.config import airline_group

CELL_KEYS = ["carrier_group", "reporting_airport", "origin_destination"]

WINDOW_MONTHS = 12
LAG_MONTHS = 4
K_CELL = 40.0
K_CARRIER = 150.0


def monthly_cell_panel(df: pl.DataFrame) -> pl.DataFrame:
    """One row per (carrier_group x airport x destination x year x month), all years.

    `df` is the arrivals frame from `analysis.base_rates.load_arrivals`.
    """
    if "carrier_group" not in df.columns:
        df = df.with_columns(
            pl.col("airline_name").map_elements(airline_group, return_dtype=pl.Utf8).alias(
                "carrier_group"
            )
        )
    panel = (
        df.group_by(CELL_KEYS + ["year", "month"])
        .agg(
            pl.col("number_flights_matched").sum().alias("n_flights"),
            (pl.col("number_flights_matched") * pl.col("p_ge_3h")).sum().alias("n_ge_3h"),
        )
        .filter(pl.col("n_flights") > 0)
        .with_columns(
            (pl.col("n_ge_3h") / pl.col("n_flights")).alias("p_ge_3h"),
            pl.date(pl.col("year"), pl.col("month"), 1).alias("date"),
        )
        .sort(CELL_KEYS + ["date"])
    )
    return panel


def _rolling_trailing(
    panel: pl.DataFrame,
    by: list[str] | None,
    window_months: int,
    lag_months: int,
    out_prefix: str,
) -> pl.DataFrame:
    """Trailing sum of n_flights/n_ge_3h over [date - window - lag, date - lag)."""
    keys = (by or []) + ["date"]
    base = (
        panel.group_by(keys)
        .agg(pl.col("n_flights").sum().alias("n_flights"), pl.col("n_ge_3h").sum().alias("n_ge_3h"))
        .sort(keys)
    )
    rolled = base.rolling(
        index_column="date",
        period=f"{window_months}mo",
        offset=f"-{window_months + lag_months}mo",
        closed="left",
        group_by=by,
    ).agg(
        pl.col("n_flights").sum().alias(f"{out_prefix}_n"),
        pl.col("n_ge_3h").sum().alias(f"{out_prefix}_ge3h"),
    )
    return base.select(keys).join(rolled, on=keys, how="left").fill_null(0)


def build_features(
    df: pl.DataFrame,
    window_months: int = WINDOW_MONTHS,
    lag_months: int = LAG_MONTHS,
    k_cell: float = K_CELL,
    k_carrier: float = K_CARRIER,
) -> pl.DataFrame:
    """Cell-month panel + trailing, point-in-time, hierarchically shrunken features.

    Shrinkage is two-level empirical Bayes (PLAN.md Phase 3 model ladder step a):
    cell rate shrunk toward its carrier's trailing rate with prior strength
    `k_cell`; carrier rate shrunk toward the global trailing rate with prior
    strength `k_carrier`. Cold-start cells/carriers (no trailing history) fall
    through cleanly to the parent level rather than being dropped.
    """
    panel = monthly_cell_panel(df)

    cell_tr = _rolling_trailing(panel, CELL_KEYS, window_months, lag_months, "cell")
    carrier_tr = _rolling_trailing(panel, ["carrier_group"], window_months, lag_months, "carrier")
    global_tr = _rolling_trailing(panel, None, window_months, lag_months, "global")

    out = (
        panel.join(cell_tr, on=CELL_KEYS + ["date"], how="left")
        .join(carrier_tr, on=["carrier_group", "date"], how="left")
        .join(global_tr, on=["date"], how="left")
    )

    out = out.with_columns(
        pl.when(pl.col("global_n") > 0)
        .then(pl.col("global_ge3h") / pl.col("global_n"))
        .otherwise(0.03)
        .alias("global_rate")
    )
    out = out.with_columns(
        (
            (pl.col("carrier_ge3h") + k_carrier * pl.col("global_rate"))
            / (pl.col("carrier_n") + k_carrier)
        ).alias("carrier_shrunken")
    )
    out = out.with_columns(
        (
            (pl.col("cell_ge3h") + k_cell * pl.col("carrier_shrunken")) / (pl.col("cell_n") + k_cell)
        ).alias("baseline_pred")
    )
    out = out.with_columns(
        (pl.col("cell_n") + 1).log().alias("log_cell_n"),
        (pl.col("carrier_n") + 1).log().alias("log_carrier_n"),
        pl.col("cell_n").gt(0).alias("has_cell_history"),
    )
    return out


FEATURE_COLS = [
    "carrier_group",
    "month",
    "log_cell_n",
    "log_carrier_n",
    "carrier_shrunken",
    "baseline_pred",
]
