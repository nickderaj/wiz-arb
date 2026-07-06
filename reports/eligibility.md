# Phase 4 — eligibility & collection haircuts (documented assumptions)

**Flagged as unvalidated (PLAN.md §5):** no published statistic gives the compensable share of 3h+ delays by cell. Every figure below is a documented assumption, not a fitted parameter — see `eligibility/haircuts.py` module docstring for sources (doc 01 §4.3, doc 04 §3/§4/§7). This is the headline sensitivity axis of the whole project; Phase 5's EV engine sweeps it.

## Cause-bucket shares of 3h+ delays, by season

| Season | Technical/crew | Weather | ATC/ATFM | Other |
| --- | ---: | ---: | ---: | ---: |
| winter | 30% | 40% | 20% | 10% |
| summer | 30% | 15% | 45% | 10% |
| shoulder | 35% | 25% | 30% | 10% |

## Within-bucket compensable (non-extraordinary) share

| Cause | Compensable share | Basis |
| --- | ---: | --- |
| Technical/crew | 85% | Wallentin-Hermann: airline-internal, rarely a sustained hidden-defect defence |
| Weather | 30% | Midpoint of doc 01 §4.3's 20-40% contestable range (ordinary weather/de-icing, BGH X ZR 146/23; reactionary knock-on, C-74/19) |
| ATC/ATFM | 8% | Paradigm 'extraordinary circumstance'; own-staff-strike carve-out (Krüsemann/C-28/20) is the rare exception |
| Other/unresolved | 45% | Unmodeled cause bucket, treated as a coin-flip-ish midpoint |

## Resulting p(non-extraordinary | delay), by season (congestion_z = 0)

| Season | p_eligible |
| --- | ---: |
| winter | 43.6% |
| summer | 38.1% |
| shoulder | 44.1% |

## Collection paths

| Path | p(paid \| valid claim) | Net multiplier (after fees) | Payout lag (months) | Basis |
| --- | ---: | ---: | ---: | --- |
| diy | 80% | 100% | 6 | DIY persistence through ADR/court; ~80% eventual success, 2-12mo (doc 04 §7) |
| agency | 90% | 65% | 3 | claims agency (e.g. AirHelp/Skycop-style); faster + higher hit rate, 35% cut |
