# Candidate shortlist — computed (doc 02 §4)

Year: 2025. Cells: carrier group x UK reporting airport x destination x month, min 100 arrivals/cell. Full table: `shortlist_2025.csv` (579 rows).

Restricted to carriers the fare model is calibrated for: Jet2.com, Ryanair, TUI Airways, Wizz Air, easyJet. Other carriers (network/long-haul) fall back to a short/medium-haul "legacy promo fare" default in the fare model that understates their real fares and would make the ranking spurious rather than conservative.

**This is a gross screening ratio, not an EV estimate:**

```
gross_screening_ratio = (p_ge_3h * K_gbp) / assumed_fare_gbp
```

- No eligibility haircut (p_e), no collection haircut (p_pi), no claim friction or time cost (phi) — those are Phase 5 (the EV engine). A ratio > 1 here is *not* a positive-EV claim.
- `K_gbp` (UK261 220/350/520) is picked from an **approximate** country-centroid distance table (`features/distance_bands.py`), not measured route distance. 0 cells were dropped (destination country not in the distance table).
- `assumed_fare_gbp` is the Phase-1 fare assumption model, not a measured fare.
- No Eurostat `avia_par_*` route-volume weighting (PLAN.md §2 item 7 not yet ingested) — thin routes are not down-weighted here.

**Deferred (not approximated on this data):** GPD tail fits and rotation-index delay-propagation analysis need flight-level data (Eurocontrol R&D / OpenSky), which has not been ingested. CAA's percentage-band CSVs are cell-level aggregates; fitting a peaks-over-threshold tail model on them would treat interval-censored aggregates as flight-level exceedances, which doc 03 §2.2 flags as invalid.

## Top 50 cells by gross screening ratio

| Carrier | UK airport | Destination | Month | n | P(3h+) | K (£) | Fare (£) | ratio |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Wizz Air | LUTON | TIRANA | 05 | 102 | 5.83% | 350 | 28.88 | 0.71 |
| easyJet | MANCHESTER | GENEVA | 01 | 118 | 6.59% | 220 | 23.80 | 0.61 |
| easyJet | MANCHESTER | PARIS (CHARLES DE GAULLE) | 01 | 117 | 4.95% | 220 | 23.80 | 0.46 |
| Ryanair | LUTON | DUBLIN | 10 | 107 | 3.74% | 220 | 18.00 | 0.46 |
| Ryanair | STANSTED | BERLIN BRANDENBURG | 02 | 101 | 2.95% | 220 | 15.30 | 0.42 |
| Ryanair | MANCHESTER | DUBLIN | 01 | 173 | 2.84% | 220 | 15.30 | 0.41 |
| easyJet | MANCHESTER | AMSTERDAM | 01 | 129 | 4.41% | 220 | 23.80 | 0.41 |
| easyJet | GATWICK | GENEVA | 01 | 210 | 3.81% | 220 | 23.80 | 0.35 |
| Ryanair | MANCHESTER | ALICANTE | 10 | 107 | 2.80% | 220 | 18.00 | 0.34 |
| Ryanair | STANSTED | BARCELONA | 07 | 124 | 4.03% | 220 | 26.10 | 0.34 |
| Ryanair | STANSTED | PISA | 08 | 103 | 3.88% | 220 | 26.10 | 0.33 |
| Ryanair | STANSTED | LISBON | 07 | 102 | 2.91% | 350 | 32.62 | 0.31 |
| easyJet | BRISTOL | GENEVA | 01 | 119 | 3.36% | 220 | 23.80 | 0.31 |
| easyJet | GATWICK | AMSTERDAM | 01 | 122 | 3.25% | 220 | 23.80 | 0.30 |
| Ryanair | STANSTED | BERGAMO | 07 | 120 | 3.33% | 220 | 26.10 | 0.28 |
| easyJet | GATWICK | PALMA DE MALLORCA | 09 | 179 | 3.91% | 220 | 30.80 | 0.28 |
| easyJet | MANCHESTER | BELFAST INTERNATIONAL | 10 | 113 | 3.51% | 220 | 28.00 | 0.28 |
| Ryanair | STANSTED | BARCELONA | 09 | 120 | 2.46% | 220 | 19.80 | 0.27 |
| easyJet | GATWICK | MILAN (MALPENSA) | 06 | 149 | 3.97% | 220 | 35.00 | 0.25 |
| Ryanair | EDINBURGH | DUBLIN | 01 | 115 | 1.70% | 220 | 15.30 | 0.24 |
| easyJet | GATWICK | NICE | 07 | 156 | 4.22% | 220 | 40.60 | 0.23 |
| Ryanair | STANSTED | ALICANTE | 07 | 111 | 2.70% | 220 | 26.10 | 0.23 |
| easyJet | GATWICK | PALMA DE MALLORCA | 06 | 166 | 3.59% | 220 | 35.00 | 0.23 |
| Ryanair | STANSTED | ALICANTE | 10 | 109 | 1.83% | 220 | 18.00 | 0.22 |
| Wizz Air | LUTON | TIRANA | 08 | 121 | 2.48% | 350 | 39.88 | 0.22 |
| easyJet | GATWICK | BARCELONA | 06 | 118 | 3.39% | 220 | 35.00 | 0.21 |
| Wizz Air | LUTON | BUCHAREST (OTOPENI) | 09 | 109 | 1.83% | 350 | 30.25 | 0.21 |
| easyJet | GATWICK | LYON | 12 | 103 | 2.91% | 220 | 30.80 | 0.21 |
| easyJet | LUTON | PALMA DE MALLORCA | 09 | 107 | 2.74% | 220 | 30.80 | 0.20 |
| easyJet | GATWICK | MILAN (MALPENSA) | 09 | 148 | 2.68% | 220 | 30.80 | 0.19 |
| easyJet | BELFAST INTERNATIONAL | LIVERPOOL (JOHN LENNON) | 09 | 110 | 2.68% | 220 | 30.80 | 0.19 |
| easyJet | MANCHESTER | GENEVA | 12 | 107 | 2.66% | 220 | 30.80 | 0.19 |
| Ryanair | STANSTED | BUDAPEST | 09 | 117 | 1.71% | 220 | 19.80 | 0.19 |
| easyJet | GATWICK | BARCELONA | 12 | 115 | 2.61% | 220 | 30.80 | 0.19 |
| Ryanair | STANSTED | DUBLIN | 01 | 234 | 1.26% | 220 | 15.30 | 0.18 |
| easyJet | EDINBURGH | STANSTED | 11 | 103 | 1.92% | 220 | 23.80 | 0.18 |
| easyJet | GATWICK | BELFAST INTERNATIONAL | 01 | 106 | 1.83% | 220 | 23.80 | 0.17 |
| easyJet | GATWICK | PALMA DE MALLORCA | 04 | 139 | 2.16% | 220 | 28.00 | 0.17 |
| easyJet | BELFAST INTERNATIONAL | EDINBURGH | 01 | 105 | 1.82% | 220 | 23.80 | 0.17 |
| easyJet | BELFAST INTERNATIONAL | GATWICK | 01 | 107 | 1.82% | 220 | 23.80 | 0.17 |
| Ryanair | STANSTED | BUCHAREST (OTOPENI) | 02 | 111 | 0.90% | 350 | 19.12 | 0.16 |
| easyJet | GATWICK | MILAN (MALPENSA) | 04 | 145 | 2.07% | 220 | 28.00 | 0.16 |
| easyJet | GATWICK | MALAGA | 10 | 147 | 2.03% | 220 | 28.00 | 0.16 |
| easyJet | GATWICK | NICE | 08 | 171 | 2.92% | 220 | 40.60 | 0.16 |
| Wizz Air | LUTON | TIRANA | 07 | 115 | 1.74% | 350 | 39.88 | 0.15 |
| Ryanair | STANSTED | LISBON | 10 | 101 | 0.98% | 350 | 22.50 | 0.15 |
| easyJet | GATWICK | NICE | 09 | 141 | 2.13% | 220 | 30.80 | 0.15 |
| easyJet | GATWICK | JERSEY | 03 | 115 | 1.74% | 220 | 25.20 | 0.15 |
| Ryanair | STANSTED | BUCHAREST (OTOPENI) | 04 | 103 | 0.97% | 350 | 22.50 | 0.15 |
| easyJet | GATWICK | MILAN (MALPENSA) | 08 | 145 | 2.72% | 220 | 40.60 | 0.15 |
