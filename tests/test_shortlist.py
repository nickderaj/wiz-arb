import polars as pl
import pytest

from wizarb.analysis.shortlist import build_shortlist
from wizarb.features.distance_bands import approx_km_from_uk, comp_band_gbp, is_long_route


def test_distance_bands():
    assert approx_km_from_uk("FRANCE") == pytest.approx(350)
    assert approx_km_from_uk("NARNIA") is None
    assert comp_band_gbp(approx_km_from_uk("IRISH REPUBLIC")) == 220.0  # short-haul
    assert comp_band_gbp(approx_km_from_uk("ROMANIA")) == 350.0  # mid-haul
    assert comp_band_gbp(approx_km_from_uk("UNITED ARAB EMIRATES")) == 520.0  # long-haul
    assert comp_band_gbp(None) is None
    assert is_long_route(approx_km_from_uk("FRANCE")) is False
    assert is_long_route(approx_km_from_uk("ROMANIA")) is True


def _flight_row(carrier, airport, dest, country, month, n, p3h):
    return {
        "airline_name": carrier,
        "reporting_airport": airport,
        "origin_destination": dest,
        "origin_destination_country": country,
        "arrival_departure": "A",
        "month": month,
        "year": 2024,
        "number_flights_matched": n,
        "number_flights_cancelled": 0,
        "p_ge_3h": p3h,
        "average_delay_mins": 20.0,
    }


def test_build_shortlist_ranks_and_drops_unmapped_country():
    from wizarb.config import airline_group

    rows = [
        _flight_row("WIZZ AIR", "LUTON", "BUCHAREST (OTOPENI)", "ROMANIA", 7, 200, 0.05),
        _flight_row("RYANAIR", "STANSTED", "DUBLIN", "IRISH REPUBLIC", 7, 200, 0.01),
        _flight_row("WIZZ AIR", "LUTON", "MYSTERYLAND", "NARNIA", 7, 200, 0.20),
    ]
    df = pl.DataFrame(rows).with_columns(
        pl.col("airline_name")
        .map_elements(airline_group, return_dtype=pl.Utf8)
        .alias("carrier_group"),
        (pl.col("number_flights_matched") * pl.col("p_ge_3h")).alias("n_ge_3h"),
        (pl.col("number_flights_matched") * pl.col("average_delay_mins")).alias(
            "delay_min_weighted"
        ),
    )

    ranked, n_dropped = build_shortlist(df, year=2024, min_flights=1)

    assert n_dropped == 1  # NARNIA cell dropped
    assert ranked.height == 2
    # Wizz/Romania has both a much higher p_ge_3h and a bigger K than
    # Ryanair/Ireland, so it must rank first.
    assert ranked.row(0, named=True)["origin_destination"] == "BUCHAREST (OTOPENI)"
