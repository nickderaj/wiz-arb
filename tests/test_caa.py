from pathlib import Path

import polars as pl
import pytest

from wizarb.config import airline_group
from wizarb.fares.assumptions import assumed_fare
from wizarb.ingest import caa

FIXTURE = Path(__file__).parent / "fixtures" / "caa_sample.csv"


def test_airline_grouping():
    assert airline_group("WIZZ AIR MALTA") == "Wizz Air"
    assert airline_group("WIZZ AIR UK") == "Wizz Air"
    assert airline_group("RYANAIR UK") == "Ryanair"
    assert airline_group("EASYJET EUROPE") == "easyJet"
    assert airline_group("AIR BALTIC") == "Air Baltic"


def test_parse_fixture():
    df = caa.parse_file(FIXTURE)
    assert df.height == 6
    assert df.get_column("reporting_period").unique().to_list() == [202407]
    wizz = df.filter(
        (pl.col("airline_name") == "WIZZ AIR") & (pl.col("arrival_departure") == "A")
    )
    assert wizz.height == 1
    row = wizz.row(0, named=True)
    assert row["number_flights_matched"] == 14
    assert row["flights_between_181_and_360_minutes_late_percent"] == pytest.approx(0.0)


def test_build_panel(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "202407_full_analysis_arrival_departure.csv").write_bytes(FIXTURE.read_bytes())
    out = caa.build_panel(raw_dir=raw, out=tmp_path / "panel.parquet")
    panel = pl.read_parquet(out)
    assert {"year", "month", "p_ge_3h"} <= set(panel.columns)
    assert panel.get_column("year").unique().to_list() == [2024]
    baltic_arr = panel.filter(
        (pl.col("airline_name") == "AIR BALTIC") & (pl.col("arrival_departure") == "A")
    ).row(0, named=True)
    # 11.111111% in the 181-360 band, 0% beyond
    assert baltic_arr["p_ge_3h"] == pytest.approx(0.11111111, rel=1e-4)


def test_assumed_fares_seasonality():
    jan = assumed_fare("Wizz Air", 1)
    jul = assumed_fare("Wizz Air", 7)
    assert jul.fare_gbp > jan.fare_gbp
    assert assumed_fare("Wizz Air", 7, long_route=True).fare_gbp > jul.fare_gbp
    assert "assumed" in jan.basis
