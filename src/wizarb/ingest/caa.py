"""UK CAA punctuality statistics: link discovery, download, and parsing.

The CAA publishes monthly and annual CSVs per year at
https://www.caa.co.uk/data-and-analysis/uk-aviation-market/flight-punctuality/uk-flight-punctuality-statistics/<year>/

We ingest the "Full Analysis Arrival Departure" CSVs: one row per
(reporting airport x origin/destination x airline x arrival/departure x
scheduled/charter), with delay-band percentage columns including 181-360 min
and >360 min - i.e. P(delay >= 3h) is directly computable. EU261 turns on
*arrival* delay, so keeping the A/D split matters.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

import httpx
import polars as pl

from wizarb.config import DATA_INTERIM, DATA_RAW

log = logging.getLogger(__name__)

BASE = "https://www.caa.co.uk"
YEAR_PAGE = (
    BASE
    + "/data-and-analysis/uk-aviation-market/flight-punctuality/"
    + "uk-flight-punctuality-statistics/{year}/"
)
RAW_DIR = DATA_RAW / "caa"

# e.g. "202407 Punctuality Statistics Full Analysis Arrival Departure (CSV, 1.00 MB)"
#      "2024 Annual Punctuality Statistics Full Analysis Arrival Departure (CSV, 2.00 MB)"
_LINK_RE = re.compile(
    r'<a[^>]+href="(?P<href>/Documents/Download/[^"]+)"[^>]*>(?P<label>.*?)</a>',
    re.S,
)
_LABEL_RE = re.compile(
    r"^(?P<period>\d{6}|\d{4})\s+(Annual\s+)?Punctuality Statistics"
    r"\s+Full Analysis Arrival Departure\s*\(CSV",
    re.I,
)

_HEADERS = {"User-Agent": "wizarb-research/0.1 (EU261 delay research; contact: repo owner)"}


def discover(year: int, client: httpx.Client | None = None) -> dict[str, str]:
    """Return {period: absolute_url} for a year's Arrival/Departure CSVs.

    period is 'YYYYMM' for monthly files or 'YYYY' for the annual file.
    """
    own = client is None
    client = client or httpx.Client(headers=_HEADERS, timeout=60, follow_redirects=True)
    try:
        resp = client.get(YEAR_PAGE.format(year=year))
        resp.raise_for_status()
        out: dict[str, str] = {}
        for m in _LINK_RE.finditer(resp.text):
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group("label"))).strip()
            lm = _LABEL_RE.match(label)
            if lm:
                out[lm.group("period")] = BASE + m.group("href")
        if not out:
            log.warning("no Arrival/Departure CSV links found for %s", year)
        return out
    finally:
        if own:
            client.close()


def download(years: list[int], dest: Path = RAW_DIR, sleep_s: float = 0.5) -> list[Path]:
    """Idempotently download all A/D CSVs for the given years into dest."""
    dest.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    with httpx.Client(headers=_HEADERS, timeout=120, follow_redirects=True) as client:
        for year in years:
            links = discover(year, client)
            for period, url in sorted(links.items()):
                out = dest / f"{period}_full_analysis_arrival_departure.csv"
                paths.append(out)
                if out.exists() and out.stat().st_size > 0:
                    continue
                log.info("downloading %s -> %s", url, out.name)
                resp = client.get(url)
                resp.raise_for_status()
                body = resp.content
                if not body.lstrip(b"\xef\xbb\xbf").startswith(b"run_date"):
                    log.warning("%s does not look like a CAA CSV; skipping", out.name)
                    continue
                out.write_bytes(body)
                time.sleep(sleep_s)
    return [p for p in paths if p.exists()]


# Columns kept from the raw files (percentages are of matched flights).
_KEEP = {
    "reporting_period": pl.Int64,
    "reporting_airport": pl.Utf8,
    "origin_destination_country": pl.Utf8,
    "origin_destination": pl.Utf8,
    "airline_name": pl.Utf8,
    "arrival_departure": pl.Utf8,
    "scheduled_charter": pl.Utf8,
    "number_flights_matched": pl.Int64,
    "number_flights_cancelled": pl.Int64,
    "flights_between_121_and_180_minutes_late_percent": pl.Float64,
    "flights_between_181_and_360_minutes_late_percent": pl.Float64,
    "flights_more_than_360_minutes_late_percent": pl.Float64,
    "flights_cancelled_percent": pl.Float64,
    "average_delay_mins": pl.Float64,
}


def parse_file(path: Path) -> pl.DataFrame:
    """Parse one raw CAA CSV into the normalized schema (monthly rows only)."""
    # all utf8, cast explicitly; some pre-2023 files contain non-UTF-8 bytes
    df = pl.read_csv(path, infer_schema_length=0, encoding="utf8-lossy")
    missing = [c for c in _KEEP if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing expected columns {missing}")
    return df.select(
        [pl.col(c).cast(t, strict=False).alias(c) for c, t in _KEEP.items()]
    )


def build_panel(raw_dir: Path = RAW_DIR, out: Path | None = None) -> Path:
    """Concatenate monthly raw files into data/interim/caa_punctuality.parquet.

    Annual files (6-digit period check fails) are excluded: they duplicate the
    monthly rows and would double-count.
    """
    out = out or DATA_INTERIM / "caa_punctuality.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(raw_dir.glob("*_full_analysis_arrival_departure.csv"))
    monthly = [p for p in files if re.match(r"^\d{6}_", p.name)]
    if not monthly:
        raise FileNotFoundError(f"no monthly CAA CSVs in {raw_dir}; run download first")
    frames = [parse_file(p) for p in monthly]
    panel = pl.concat(frames, how="vertical")
    panel = panel.with_columns(
        (pl.col("reporting_period") // 100).alias("year"),
        (pl.col("reporting_period") % 100).alias("month"),
        (
            (
                pl.col("flights_between_181_and_360_minutes_late_percent").fill_null(0)
                + pl.col("flights_more_than_360_minutes_late_percent").fill_null(0)
            )
            / 100.0
        ).alias("p_ge_3h"),
    )
    panel.write_parquet(out)
    log.info("wrote %s (%d rows, %d files)", out, panel.height, len(monthly))
    return out
