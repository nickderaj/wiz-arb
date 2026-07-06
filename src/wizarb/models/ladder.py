"""Model ladder step (b)/(c): weighted logistic regression and gradient boosting.

Each cell-month row is a binomial trial (`n_ge_3h` of `n_flights`). Both
sklearn's `LogisticRegression` and `HistGradientBoostingClassifier` expect
per-observation 0/1 labels with weights, not raw binomial counts, so we expand
every row into two weighted pseudo-observations (success/failure) — this is
algebraically equivalent to weighted binomial GLM fitting (each pseudo-row
contributes its share of the binomial log-likelihood) and avoids adding a
statsmodels dependency for a single feature.

**Substitution note:** PLAN.md's model ladder step (c) names LightGBM. This
repo's macOS/uv environment lacks the `libomp` runtime LightGBM's compiled
extension requires, and installing it means reaching outside the project
(Homebrew, system libs) for a research script. `HistGradientBoostingClassifier`
fills the same ladder role (histogram-based gradient-boosted trees, native
categorical support) with zero native-library risk; swap in LightGBM later if
the environment gets `libomp`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from wizarb.models.features import FEATURE_COLS

NUMERIC_COLS = [c for c in FEATURE_COLS if c not in ("carrier_group", "month")]
CATEGORICAL_COLS = ["carrier_group", "month"]


def _expand(df: pl.DataFrame) -> tuple[pl.DataFrame, np.ndarray, np.ndarray]:
    """Row -> two weighted pseudo-rows (label=1 weight=n_ge_3h, label=0 weight=n_flights-n_ge_3h)."""
    n = df.get_column("n_flights").to_numpy()
    pos = df.get_column("n_ge_3h").to_numpy()
    neg = n - pos
    X = pl.concat([df, df])
    y = np.concatenate([np.ones(len(df)), np.zeros(len(df))])
    w = np.concatenate([pos, neg])
    keep = w > 0
    return X.filter(pl.Series(keep)), y[keep], w[keep]


def _pipeline(estimator) -> Pipeline:
    ct = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS)],
        remainder="passthrough",
    )
    return Pipeline([("ct", ct), ("est", estimator)])


@dataclass
class FittedModel:
    name: str
    pipeline: Pipeline

    def predict(self, df: pl.DataFrame) -> np.ndarray:
        X = df.select(FEATURE_COLS).to_pandas()
        return self.pipeline.predict_proba(X)[:, 1]


def fit_logistic(train: pl.DataFrame) -> FittedModel:
    Xw, y, w = _expand(train)
    X = Xw.select(FEATURE_COLS).to_pandas()
    pipe = _pipeline(LogisticRegression(max_iter=1000))
    pipe.fit(X, y, est__sample_weight=w)
    return FittedModel("logistic", pipe)


def fit_gbm(train: pl.DataFrame) -> FittedModel:
    Xw, y, w = _expand(train)
    X = Xw.select(FEATURE_COLS).to_pandas()
    est = HistGradientBoostingClassifier(
        max_iter=200,
        max_leaf_nodes=15,
        min_samples_leaf=50,
        learning_rate=0.05,
    )
    pipe = _pipeline(est)
    pipe.fit(X, y, est__sample_weight=w)
    return FittedModel("gbm", pipe)
