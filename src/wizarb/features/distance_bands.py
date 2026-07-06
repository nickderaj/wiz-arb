"""Approximate great-circle distance bands, for EU261/UK261 compensation tiers only.

CAA data gives destination as a country + city name, not coordinates, so there
is no measured route distance to join against. This module hardcodes an
approximate London-centroid great-circle distance (km) per destination
country, rounded to the nearest 50km from public reference distances. It
exists solely to pick a compensation band (<=1500km / 1500-3500km / >3500km);
it is NOT a substitute for per-route distance and should not be used for
anything else. Countries not covered return `None` and must be excluded from
distance-dependent analysis rather than defaulted, since guessing a band
silently would misprice the shortlist ranking.

Flights out of UK reporting airports fall under UK261 (Air Passenger Rights
Regulations), which pays GBP 220/350/520 at the same 1,500/3,500 km breakpoints
as EU261's EUR 250/400/600 -- see PLAN.md section 0. The fare model
(fares/assumptions.py) is GBP-denominated, so we band in GBP for currency
consistency with the screening ratio.
"""

from __future__ import annotations

# Approximate km from London to the destination country's principal
# civil-aviation city, for banding purposes only. Values are rounded
# reference great-circle distances, not measured route distances. Keys use
# the CAA's own country spellings (checked against the ingested panel, which
# uses e.g. "IRISH REPUBLIC" and "SLOVAK REPUBLIC", not "IRELAND"/"SLOVAKIA")
# -- a plain-name table silently drops most of Ireland/Portugal/Slovakia/
# Serbia/Montenegro/Moldova traffic via a lookup miss, not a stated exclusion.
_COUNTRY_KM_FROM_UK: dict[str, float] = {
    "UNITED KINGDOM": 400,  # domestic
    "IRISH REPUBLIC": 450,
    "FRANCE": 350,
    "BELGIUM": 320,
    "NETHERLANDS": 360,
    "LUXEMBOURG": 500,
    "GERMANY": 800,
    "SWITZERLAND": 750,
    "AUSTRIA": 1200,
    "DENMARK": 950,
    "NORWAY": 1150,
    "SWEDEN": 1450,
    "FINLAND": 1900,
    "ICELAND": 1900,
    "POLAND": 1450,
    "CZECH REPUBLIC": 1050,
    "SLOVAK REPUBLIC": 1300,
    "HUNGARY": 1450,
    "ROMANIA": 2100,
    "BULGARIA": 2400,
    "CROATIA": 1650,
    "SLOVENIA": 1350,
    "BOSNIA-HERZEGOVINA": 1750,
    "REPUBLIC OF SERBIA": 1900,
    "REPUBLIC OF MONTENEGRO": 1950,
    "ALBANIA": 2050,
    "GREECE": 2400,
    "CYPRUS": 3400,
    "TURKEY": 2500,
    "ITALY": 1400,
    "SPAIN": 1250,
    "SPAIN(CANARY ISLANDS)": 3100,
    "PORTUGAL(EXCLUDING MADEIRA)": 1600,
    "PORTUGAL(MADEIRA)": 2500,
    "MALTA": 2100,
    "MOROCCO": 2050,
    "TUNISIA": 1850,
    "ALGERIA": 1900,
    "EGYPT": 3500,
    "ISRAEL": 3600,
    "JORDAN": 3600,
    "LEBANON": 3500,
    "UNITED ARAB EMIRATES": 5500,
    "UKRAINE": 2100,
    "BELARUS": 1900,
    "LATVIA": 1700,
    "LITHUANIA": 1600,
    "ESTONIA": 1850,
    "GEORGIA": 3200,
    "ARMENIA": 3600,
    "AZERBAIJAN": 3900,
    "RUSSIA": 2500,
    "REPUBLIC OF MOLDOVA": 2050,
    "NORTH MACEDONIA": 2100,
    "GIBRALTAR": 1700,
    "FAROE ISLANDS": 1250,
    # Longer-haul destinations served by non-ULCC carriers in the panel
    # (BA/Jet2/TUI/charter) -- precision beyond the >3,500 km breakpoint
    # doesn't matter for banding, so these are coarse.
    "USA": 5500,
    "CANADA": 5500,
    "MEXICO": 8900,
    "BRAZIL": 9400,
    "QATAR": 5200,
    "SAUDI ARABIA": 4900,
    "BAHRAIN": 5100,
    "KUWAIT": 4700,
    "OMAN": 5700,
    "INDIA": 6700,
    "PAKISTAN": 6300,
    "SRI LANKA": 8700,
    "CHINA": 8100,
    "HONG KONG": 9600,
    "SINGAPORE": 10800,
    "MALAYSIA": 10600,
    "THAILAND": 9500,
    "TAIWAN": 9700,
    "REPUBLIC OF KOREA": 8900,
    "JAPAN": 9500,
    "AUSTRALIA": 17000,
    "REPUBLIC OF SOUTH AFRICA": 9000,
    "KENYA": 6800,
    "ETHIOPIA": 5900,
    "NIGERIA": 5000,
    "GHANA": 5100,
    "CAPE VERDE ISLANDS": 4700,
    "BARBADOS": 6800,
    "JAMAICA": 7600,
    "DOMINICAN REPUBLIC": 6900,
    "MAURITIUS": 9800,
}

# UK261 bands (GBP), breakpoints at 1,500 km and 3,500 km (mirrors EU261's
# EUR 250/400/600 at the same distance breaks -- PLAN.md section 0).
_BAND_SHORT_GBP = 220.0
_BAND_MID_GBP = 350.0
_BAND_LONG_GBP = 520.0
SHORT_HAUL_KM = 1500.0
LONG_HAUL_KM = 3500.0


def approx_km_from_uk(country: str | None) -> float | None:
    """Approximate great-circle km from the UK to `country`'s civil-aviation centroid.

    Returns None for countries not in the reference table (not a band guess).
    """
    if country is None:
        return None
    km = _COUNTRY_KM_FROM_UK.get(country.strip().upper())
    return float(km) if km is not None else None


def comp_band_gbp(km: float | None) -> float | None:
    """UK261 compensation tier (GBP) for a given approximate distance."""
    if km is None:
        return None
    if km <= SHORT_HAUL_KM:
        return _BAND_SHORT_GBP
    if km <= LONG_HAUL_KM:
        return _BAND_MID_GBP
    return _BAND_LONG_GBP


def is_long_route(km: float | None) -> bool:
    """True once distance clears the mid/long compensation breakpoint (for the fare model)."""
    return km is not None and km > SHORT_HAUL_KM
