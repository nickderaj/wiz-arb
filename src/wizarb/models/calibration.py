"""Calibration and scoring against a binomial cell-rate target.

`actual` here is a cell's realized `p_ge_3h` (a rate, not a 0/1 label), and
`weight` is `n_flights`. Weighted MSE between a predicted rate and an observed
binomial rate is a cell-level proxy for the per-flight Brier score: the true
per-flight Brier decomposes as `(pred - actual)^2 + actual*(1-actual)/n`
(finite-sample binomial variance), so this understates the flight-level Brier
slightly for small cells. It is reported as `brier_proxy`, not `brier`, to keep
that distinction visible in every report.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl
from sklearn.isotonic import IsotonicRegression


def brier_proxy(actual: np.ndarray, pred: np.ndarray, weight: np.ndarray) -> float:
    return float(np.average((pred - actual) ** 2, weights=weight))


def log_loss_weighted(actual: np.ndarray, pred: np.ndarray, weight: np.ndarray, eps: float = 1e-6) -> float:
    p = np.clip(pred, eps, 1 - eps)
    ll = -(actual * np.log(p) + (1 - actual) * np.log(1 - p))
    return float(np.average(ll, weights=weight))


def reliability_table(actual: np.ndarray, pred: np.ndarray, weight: np.ndarray, n_bins: int = 10) -> pl.DataFrame:
    edges = np.quantile(pred, np.linspace(0, 1, n_bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    bin_idx = np.digitize(pred, edges[1:-1], right=True)
    rows = []
    for b in range(n_bins):
        mask = bin_idx == b
        if not mask.any():
            continue
        rows.append(
            {
                "bin": b,
                "n_cells": int(mask.sum()),
                "weight_sum": float(weight[mask].sum()),
                "mean_pred": float(np.average(pred[mask], weights=weight[mask])),
                "mean_actual": float(np.average(actual[mask], weights=weight[mask])),
            }
        )
    return pl.DataFrame(rows)


@dataclass
class Calibrator:
    iso: IsotonicRegression

    def apply(self, pred: np.ndarray) -> np.ndarray:
        return self.iso.predict(pred)


def fit_isotonic(pred: np.ndarray, actual: np.ndarray, weight: np.ndarray) -> Calibrator:
    """Fit on a nested out-of-time fold (the caller passes only that fold's rows)."""
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(pred, actual, sample_weight=weight)
    return Calibrator(iso)
