"""Paths and shared constants."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_INTERIM = REPO_ROOT / "data" / "interim"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
REPORTS = REPO_ROOT / "reports"

# Airline-group prefixes: the CAA reports each AOC separately (e.g. Wizz Air
# operates in the UK as Wizz Air UK / Hungary / Malta). Grouping is by
# case-insensitive prefix match on `airline_name`.
AIRLINE_GROUPS: dict[str, list[str]] = {
    "Wizz Air": ["WIZZ"],
    "Ryanair": ["RYANAIR"],
    "easyJet": ["EASYJET"],
    "TUI Airways": ["TUI AIRWAYS", "TUI FLY"],
    "Jet2.com": ["JET2"],
    "British Airways": ["BRITISH AIRWAYS", "BA CITYFLYER", "BA EUROFLYER"],
    "Vueling": ["VUELING"],
    "Aer Lingus": ["AER LINGUS"],
}


def airline_group(name: str) -> str:
    """Map a raw CAA airline_name to a carrier group; fall back to the raw name."""
    up = name.upper().strip()
    for group, prefixes in AIRLINE_GROUPS.items():
        if any(up.startswith(p) for p in prefixes):
            return group
    return name.strip().title()
