import polars as pl

from wizarb.models.calibration import brier_proxy, fit_isotonic, log_loss_weighted, reliability_table
from wizarb.models.features import build_features
from wizarb.models.walkforward import run_walkforward


def _synthetic_arrivals(n_years=4, n_months=12, n_flights=100) -> pl.DataFrame:
    rows = []
    for year in range(2020, 2020 + n_years):
        for month in range(1, n_months + 1):
            # Carrier A: stable ~10% rate. Carrier B: stable ~2% rate.
            rows.append(
                {
                    "airline_name": "WIZZ AIR",
                    "carrier_group": "Wizz Air",
                    "reporting_airport": "LUTON",
                    "origin_destination": "TIRANA",
                    "year": year,
                    "month": month,
                    "number_flights_matched": n_flights,
                    "p_ge_3h": 0.10,
                }
            )
            rows.append(
                {
                    "airline_name": "RYANAIR",
                    "carrier_group": "Ryanair",
                    "reporting_airport": "STANSTED",
                    "origin_destination": "DUBLIN",
                    "year": year,
                    "month": month,
                    "number_flights_matched": n_flights,
                    "p_ge_3h": 0.02,
                }
            )
    return pl.DataFrame(rows)


def test_build_features_shrinkage_and_point_in_time():
    df = _synthetic_arrivals()
    feats = build_features(df)

    # No feature should require future data: every row's trailing counts must
    # come only from strictly earlier months (enforced by construction, but
    # assert the shape here as a regression guard).
    assert feats.height == df.height

    late = feats.filter((pl.col("year") == 2023) & (pl.col("month") == 6))
    wizz = late.filter(pl.col("carrier_group") == "Wizz Air").row(0, named=True)
    ryan = late.filter(pl.col("carrier_group") == "Ryanair").row(0, named=True)

    # With enough trailing history, shrunken predictions should sit close to
    # each carrier's true stable rate and be clearly ordered.
    assert wizz["baseline_pred"] > ryan["baseline_pred"]
    assert 0.05 < wizz["baseline_pred"] < 0.15
    assert 0.0 < ryan["baseline_pred"] < 0.05

    early = feats.filter((pl.col("year") == 2020) & (pl.col("month") == 1))
    assert not early.get_column("has_cell_history").any()


def test_calibration_metrics():
    actual = pl.Series([0.1, 0.2, 0.05]).to_numpy()
    pred = pl.Series([0.12, 0.18, 0.05]).to_numpy()
    weight = pl.Series([100.0, 100.0, 100.0]).to_numpy()

    assert brier_proxy(actual, pred, weight) >= 0
    assert log_loss_weighted(actual, pred, weight) >= 0
    tbl = reliability_table(actual, pred, weight, n_bins=3)
    assert tbl.height <= 3

    cal = fit_isotonic(pred, actual, weight)
    out = cal.apply(pred)
    assert out.shape == pred.shape


def test_walkforward_runs_and_scores_all_models():
    df = _synthetic_arrivals()
    feats = build_features(df)
    results, reliability = run_walkforward(feats, first_test_year=2022, last_test_year=2023)

    assert set(results.get_column("model").unique().to_list()) == {"baseline", "logistic", "gbm"}
    assert results.filter(pl.col("test_year") == 2023).height > 0
    assert "baseline" in reliability
    assert "logistic_calibrated" in reliability
    assert "gbm_calibrated" in reliability
