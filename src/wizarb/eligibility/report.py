"""Writes the documented eligibility/collection haircut table (PLAN.md Phase 4 deliverable)."""

from __future__ import annotations

import logging
from pathlib import Path

from wizarb.config import REPORTS
from wizarb.eligibility.haircuts import CAUSE_MIX, COMPENSABLE_SHARE, cause_mix, collection_outcome, eligibility_share

log = logging.getLogger(__name__)


def write_report(out_dir: Path = REPORTS) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 4 — eligibility & collection haircuts (documented assumptions)",
        "",
        "**Flagged as unvalidated (PLAN.md §5):** no published statistic gives the "
        "compensable share of 3h+ delays by cell. Every figure below is a documented "
        "assumption, not a fitted parameter — see `eligibility/haircuts.py` module "
        "docstring for sources (doc 01 §4.3, doc 04 §3/§4/§7). This is the headline "
        "sensitivity axis of the whole project; Phase 5's EV engine sweeps it.",
        "",
        "## Cause-bucket shares of 3h+ delays, by season",
        "",
        "| Season | Technical/crew | Weather | ATC/ATFM | Other |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for season, mix in CAUSE_MIX.items():
        lines.append(
            f"| {season} | {mix['technical_crew']:.0%} | {mix['weather']:.0%} "
            f"| {mix['atc_atfm']:.0%} | {mix['other']:.0%} |"
        )
    lines += [
        "",
        "## Within-bucket compensable (non-extraordinary) share",
        "",
        "| Cause | Compensable share | Basis |",
        "| --- | ---: | --- |",
        f"| Technical/crew | {COMPENSABLE_SHARE['technical_crew']:.0%} | Wallentin-Hermann: airline-internal, rarely a sustained hidden-defect defence |",
        f"| Weather | {COMPENSABLE_SHARE['weather']:.0%} | Midpoint of doc 01 §4.3's 20-40% contestable range (ordinary weather/de-icing, BGH X ZR 146/23; reactionary knock-on, C-74/19) |",
        f"| ATC/ATFM | {COMPENSABLE_SHARE['atc_atfm']:.0%} | Paradigm 'extraordinary circumstance'; own-staff-strike carve-out (Krüsemann/C-28/20) is the rare exception |",
        f"| Other/unresolved | {COMPENSABLE_SHARE['other']:.0%} | Unmodeled cause bucket, treated as a coin-flip-ish midpoint |",
        "",
        "## Resulting p(non-extraordinary | delay), by season (congestion_z = 0)",
        "",
        "| Season | p_eligible |",
        "| --- | ---: |",
    ]
    for season, months in [("winter", 1), ("summer", 7), ("shoulder", 4)]:
        lines.append(f"| {season} | {eligibility_share(months):.1%} |")
    lines += [
        "",
        "## Collection paths",
        "",
        "| Path | p(paid \\| valid claim) | Net multiplier (after fees) | Payout lag (months) | Basis |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for path in ["diy", "agency"]:
        o = collection_outcome(path)
        lines.append(
            f"| {path} | {o.p_paid:.0%} | {o.net_multiplier:.0%} | {o.payout_lag_months:.0f} | {o.basis} |"
        )
    lines.append("")

    out = out_dir / "eligibility.md"
    out.write_text("\n".join(lines))
    log.info("wrote %s", out)
    return out
