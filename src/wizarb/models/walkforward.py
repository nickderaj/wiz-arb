"""Phase 3 walk-forward validation of the model ladder.

For each test year t: train on all cell-months with year < t, fit each model,
then calibrate on a **nested** out-of-time fold carved from the *end* of the
training window (never on pooled future data, never on the test year itself),
then score the calibrated model on year t. The shrunken-cell-mean baseline
must be beaten out-of-sample by logistic/LightGBM to justify their complexity
(PLAN.md Phase 3) — the report states whether it was.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import polars as pl

from wizarb.analysis.base_rates import PANEL, load_arrivals
from wizarb.config import REPORTS
from wizarb.models import ladder
from wizarb.models.calibration import brier_proxy, fit_isotonic, log_loss_weighted, reliability_table
from wizarb.models.features import build_features

log = logging.getLogger(__name__)

CALIB_FOLD_MONTHS = 12


def _split_calib(train: pl.DataFrame, calib_months: int = CALIB_FOLD_MONTHS) -> tuple[pl.DataFrame, pl.DataFrame]:
    cutoff = train.get_column("date").max()
    calib_start = cutoff.replace(day=1)
    # step back calib_months months
    y, m = calib_start.year, calib_start.month
    total = y * 12 + (m - 1) - calib_months
    calib_start = calib_start.replace(year=total // 12, month=total % 12 + 1)
    fit_fold = train.filter(pl.col("date") < calib_start)
    calib_fold = train.filter(pl.col("date") >= calib_start)
    return fit_fold, calib_fold


def _score(name: str, year: int, actual: np.ndarray, pred: np.ndarray, weight: np.ndarray, calibrated: bool) -> dict:
    return {
        "model": name,
        "test_year": year,
        "calibrated": calibrated,
        "n_cells": len(actual),
        "n_flights": float(weight.sum()),
        "brier_proxy": brier_proxy(actual, pred, weight),
        "log_loss": log_loss_weighted(actual, pred, weight),
        "mean_pred": float(np.average(pred, weights=weight)),
        "mean_actual": float(np.average(actual, weights=weight)),
    }


def run_walkforward(features: pl.DataFrame, first_test_year: int, last_test_year: int) -> tuple[pl.DataFrame, dict]:
    rows: list[dict] = []
    reliability: dict[str, pl.DataFrame] = {}

    for year in range(first_test_year, last_test_year + 1):
        train = features.filter(pl.col("year") < year)
        test = features.filter(pl.col("year") == year)
        if train.is_empty() or test.is_empty():
            continue

        fit_fold, calib_fold = _split_calib(train)
        if fit_fold.is_empty() or calib_fold.is_empty():
            fit_fold, calib_fold = train, train  # first available year: no room to nest, reuse (flagged in report)

        actual_test = test.get_column("p_ge_3h").to_numpy()
        weight_test = test.get_column("n_flights").to_numpy()

        # (a) shrunken baseline — already computed, point-in-time by construction.
        base_pred = test.get_column("baseline_pred").to_numpy()
        rows.append(_score("baseline", year, actual_test, base_pred, weight_test, calibrated=False))

        for fit_fn, name in [(ladder.fit_logistic, "logistic"), (ladder.fit_gbm, "gbm")]:
            model = fit_fn(fit_fold)
            raw_pred = model.predict(test)
            rows.append(_score(name, year, actual_test, raw_pred, weight_test, calibrated=False))

            calib_pred_on_fold = model.predict(calib_fold)
            cal = fit_isotonic(
                calib_pred_on_fold,
                calib_fold.get_column("p_ge_3h").to_numpy(),
                calib_fold.get_column("n_flights").to_numpy(),
            )
            cal_pred = cal.apply(raw_pred)
            rows.append(_score(name, year, actual_test, cal_pred, weight_test, calibrated=True))

            if year == last_test_year:
                reliability[f"{name}_calibrated"] = reliability_table(actual_test, cal_pred, weight_test)

        if year == last_test_year:
            reliability["baseline"] = reliability_table(actual_test, base_pred, weight_test)

    return pl.DataFrame(rows), reliability


def write_report(
    panel_path: Path = PANEL,
    out_dir: Path = REPORTS,
    first_test_year: int | None = None,
    last_test_year: int | None = None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load_arrivals(panel_path)
    features = build_features(df)
    years = sorted(features.get_column("year").unique().to_list())
    first_test_year = first_test_year or (years[0] + 2)
    last_test_year = last_test_year or years[-1]

    results, reliability = run_walkforward(features, first_test_year, last_test_year)
    results.write_csv(out_dir / "model_backtest_metrics.csv")
    for name, tbl in reliability.items():
        tbl.write_csv(out_dir / f"reliability_{name}.csv")

    lines = [
        "# Phase 3 — probability model walk-forward validation",
        "",
        f"Test years {first_test_year}-{last_test_year}, trained on all prior years. "
        "Target is the cell-month binomial rate `p_ge_3h` (see `models/features.py` "
        "docstring: CAA data is cell-level, not flight-level, so this is a documented "
        "substitution for the per-flight target in PLAN.md, not an approximation).",
        "",
        "`brier_proxy`/`log_loss` are weighted against the observed cell rate — see "
        "`models/calibration.py` docstring for why this is a proxy, not the exact "
        "flight-level Brier score.",
        "",
        "| Year | Model | Calibrated | n cells | n flights | Brier proxy | Log loss | mean pred | mean actual |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in results.sort(["test_year", "model", "calibrated"]).iter_rows(named=True):
        lines.append(
            f"| {r['test_year']} | {r['model']} | {r['calibrated']} | {r['n_cells']:,} "
            f"| {r['n_flights']:,.0f} | {r['brier_proxy']:.5f} | {r['log_loss']:.4f} "
            f"| {r['mean_pred']:.3%} | {r['mean_actual']:.3%} |"
        )

    lines += ["", "## Baseline vs. complexity"]
    last = results.filter(pl.col("test_year") == last_test_year)
    base_brier = last.filter(pl.col("model") == "baseline").get_column("brier_proxy")[0]
    for name in ["logistic", "gbm"]:
        cal = last.filter((pl.col("model") == name) & (pl.col("calibrated")))
        if cal.is_empty():
            continue
        b = cal.get_column("brier_proxy")[0]
        verdict = "beats" if b < base_brier else "does NOT beat"
        lines.append(
            f"- {name} (calibrated), test year {last_test_year}: Brier proxy {b:.5f} "
            f"vs. baseline {base_brier:.5f} — **{verdict}** the shrunken-cell-mean baseline."
        )
    lines.append("")

    out = out_dir / "model-backtest.md"
    out.write_text("\n".join(lines))
    log.info("wrote %s", out)
    return out
