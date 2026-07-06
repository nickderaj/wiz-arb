# European Airline Delay Statistics — Data Sources & Screening Design

**Research memo 02 — EU261/UK261 delay-compensation arbitrage project**
Date: 2026-07-05 · Status: Screening design. **No computations have been run yet** — all
route/airline delay rates in earlier drafts of this memo were removed because they had not
actually been computed from data. This memo now defines _what_ will be computed, _from which
sources_, and _which hypotheses_ the computation must confirm or refute.

> **Core question:** which airline / route / month combinations maximise
> P(arrival delay ≥ 3h or cancellation) relative to ticket price, since EU261/UK261 pays a
> fixed £220–£520 (€250–€600) when a flight arrives ≥ 3h late for reasons within the
> airline's control?

---

## 1. Primary dataset and methodology

The single best free dataset identified is the **UK CAA punctuality statistics** — monthly and
annual CSVs at **airline × UK airport × destination** granularity, with delay-band columns
including `flights_between_121_and_180_minutes_late_percent`,
`flights_between_181_and_360_minutes_late_percent` and
`flights_more_than_360_minutes_late_percent`, plus matched/cancelled flight counts. This lets
us compute **P(delay ≥ 3h)** directly rather than inferring it from average delay.
(Schema verified by downloading a sample file, July 2026.)

Planned computation (Phase 1–2 of PLAN.md): ingest the `Full_Analysis_Arrival_Departure` CSVs
(arrivals and departures split — EU261 turns on _arrival_ delay) for 2019–2025, then compute
P(3h+) and cancellation rates by airline group, airport, route, and month.

**Design caveats (established before computing, so they can't be post-hoc rationalized):**

1. The plain "Full Analysis" files pool arrivals _and_ departures at the UK reporting airport.
   Use the `Arrival_Departure` variant and filter to the relevant direction. Departure delay
   ≥ 3h is a strong but imperfect proxy for arrival delay (block-time padding recovers
   ~5–15 min on short-haul).
2. Wizz Air operates in the UK through three AOCs (Wizz Air UK, Wizz Air Hungary, Wizz Air
   Malta); Ryanair through two (Ryanair DAC, Ryanair UK); easyJet through two (easyJet UK,
   easyJet Europe). Aggregate per group; verify the exact `airline_name` strings in the data.
3. UK CAA data covers UK-touching flights only. Pan-EU coverage requires
   Eurocontrol/paid sources.
4. **Compensation haircut:** EU261 excludes "extraordinary circumstances". **No published
   statistic exists for the compensable share of 3h+ delays** — any eligibility share used in
   the EV model (working band **0.35–0.55**, from claim-industry anecdote) is an assumption
   and the headline sensitivity axis of the whole project. Weather is not a categorical
   exclusion (see doc 01 §4.3).
5. **Data freshness:** press coverage documents a Wizz Air operational turnaround in 2025
   (on-time performance up double-digit percentages year-on-year). Any screening result
   computed on 2024 data must be re-verified on 2025 data before being relied on; ingest both.

---

## 2. External published context (cited, not computed by us)

These are third-party published figures — useful priors for what the pipeline should find,
not results:

- PA/CAA 2023 analysis: Wizz Air ranked worst UK airline for average departure delay for the
  3rd consecutive year (31 min 36 s in 2023)
  ([Enfield Independent / PA](https://www.enfieldindependent.co.uk/news/national/24384336.wizz-air-ranked-worst-airline-delays-despite-soaring-fares/)).
- Which? analysis of CAA data May 2024–Apr 2025: worst on-time departure rates — TUI 59.2%,
  Wizz Air 66.0%, Ryanair 66.5%
  ([Which?](https://www.which.co.uk/news/article/why-are-so-many-flights-delayed-ak7C41l03njC)).
- Cirium OTP Review 2024 (Europe): Europe average 79.7% on-time arrivals; Wizz/Ryanair/easyJet
  absent from the top-10
  ([Cirium 2024 OTP Review PDF](https://assets.fta.cirium.com/wp-content/uploads/2025/01/02050431/2024-OTP-Annual-Review_20250101-1.pdf)).
- EU/EEA/UK 2024: ~218,000 departures (~1.5% of all departures) delayed ≥ 3h or cancelled —
  claim-industry estimate of the gross EU261-event base rate
  ([AeroTime](https://www.aerotime.aero/articles/218000-eu-flight-disruptions-may-cost-airlines-over-e6-billion-in-compensation)).
- Eurocontrol CODA: average all-causes delay per flight 17.5 min (2023 and 2024); reactionary
  delay 46% of delay minutes (2023)
  ([CODA Digest Annual 2023 PDF](https://www.eurocontrol.int/sites/default/files/2024-12/eurocontrol-coda-digest-annual-report-2023.pdf)).
- flightright's 2025 ranking places Wizz Air 3rd-worst in Europe
  ([flightright](https://flightrights.net/en/blog/airline-ranking/)).

None of these report the quantity we actually need — **P(3h+ arrival delay) per bookable
cell** — which is why the pipeline exists.

## 3. Structural delay drivers (qualitative, sourced — to be quantified)

1. **Time of day.** Delays propagate through aircraft rotations; ULCC aircraft fly 6–8
   sectors/day with 25–35 min turnarounds and no spare aircraft. US analyses show evening
   flights several times likelier to be delayed than first-wave departures
   ([Forbes](https://www.forbes.com/sites/garystoller/2019/06/03/most-flight-delays-in-the-evening-and-unrelated-to-bad-weather/),
   [Thrifty Traveler](https://thriftytraveler.com/guides/flights/data-analysis-first-flight-of-the-day/)).
   **Hypothesis: the last rotation of the day is the strongest bookable lever.** Note: CAA
   data has no time-of-day granularity — this lever must be measured from flight-level data
   (Eurocontrol R&D archive / OpenSky).
2. **Season.** June–September ATFM capacity/weather crunch; July 2024 set the all-time record
   for en-route ATFM delays (CODA). **Hypothesis: summer months multiply the 3h+ tail
   several-fold** — but summer excess delay is ATFM/weather-loaded, i.e. disproportionately
   _exempt_ (the doc 03 §3.3 adverse-selection concern).
3. **Day of week.** Friday/Sunday evening leisure peaks through slot-constrained airports.
4. **Airline ops model.** Wizz's ultra-tight scheduling, low spare-aircraft ratio and
   (2023–24) GTF-engine groundings; TUI's long charter sectors to congested leisure airports.
5. **Airport congestion.** Single-runway/slot-constrained airports (Gatwick, Luton, Lisbon,
   Naples) are repeatedly flagged in CODA monthly narratives.

## 4. Candidate screening — design (results TBD)

The pipeline will produce, per cell (airline group × route × month):

- n flights, P(3h+), P(cancelled), average delay — from CAA CSVs;
- volume weighting via Eurostat `avia_par_*` route volumes (down-weight thin routes);
- a shortlist ranked by gross expected compensation ÷ assumed fare, with explicit
  eligibility-haircut sensitivity bands.

Prior expectation (from §2 context): Wizz Air UK-touching routes to Central/Eastern Europe
and congested leisure destinations, evening departures, July–August, will screen best.
**This is a hypothesis, not a finding.** The shortlist table will be generated by code and
checked into `reports/` when Phase 2 runs.

## 5. Ticket-price reference (external, for the fare model)

No free historical fare archive exists, so the backtest uses an **assumed fare model**
(documented, conservative), plus a forward-collecting scraper for live validation:

- **Wizz Air:** promo fares £14.99–£29.99 seen on off-peak UK→Poland/Romania; DLR (German
  Aerospace Center) low-cost fare survey: Wizz average one-way fare €67 (Q1 2025), Ryanair €80
  ([DLR survey via Daily News Hungary](https://dailynewshungary.com/wizz-air-overtakes-ryanair-as-europes-cheapest-low-cost-airline/)).
  Ryanair's own filings put its network average fare near €46–50 (FY2024–25).
- **Ryanair:** regular £14.99–£24.99 seat sales; summer peak evening slots higher.
- **easyJet:** rarely below £25. **TUI:** seat-only from ~£50, rarely promotional.
- Ratio arithmetic: at a £20 fare and £220 band, compensation = 11× ticket price;
  frictionless break-even P(payout) = fare/compensation ≈ 6–11% across typical fare/band
  combinations. (Algebra, not an empirical claim.)

The fare model's bias is not neutral: fares and delay propensity are jointly driven by
season/congestion, so a static fare model can create phantom edge in peak cells — report any
backtest as conditional on the fare model.

## 6. Data sources for backtesting

| Source                            | Granularity                                                                                             | History                                                       | Cost / access                                                   | Notes                                                                                                                                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UK CAA punctuality statistics** | Airline × UK airport × destination × month; delay bands incl. 121–180, 181–360, >360 min; cancellations | 1990s→present, monthly CSVs                                   | **Free**                                                        | _The_ backtest backbone for UK-touching flights. No flight-number/time-of-day granularity. [caa.co.uk](https://www.caa.co.uk/data-and-analysis/uk-aviation-market/flight-punctuality/) |
| **Eurocontrol R&D Data Archive**  | Flight-by-flight: flight plans, actual routes, times (12M+ flights)                                     | 4 months/year (Mar/Jun/Sep/Dec), ~2-yr publication lag, 2015→ | **Free** for research (OneSky registration)                     | Actual vs scheduled times per flight → time-of-day/rotation analysis. [eurocontrol.int](https://www.eurocontrol.int/dashboard/aviation-data-research)                                  |
| **Eurocontrol CODA digests**      | Network/airport/cause aggregates, monthly                                                               | 2008→                                                         | Free                                                            | Base rates, cause splits (key for the eligibility haircut). [ansperformance.eu](https://ansperformance.eu/capacity/tot_dly/)                                                           |
| **OpenSky Network**               | Raw ADS-B state vectors; historical DB; Python `traffic` lib                                            | 2016→                                                         | Free (research account, justified application; can be declined) | Reconstruct rotations/arrival times; heavy engineering. [opensky-network.org/data](https://opensky-network.org/data)                                                                   |
| **Eurostat `avia_par_*`**         | Route-level passenger/flight volumes, EU/EFTA                                                           | 1993→                                                         | Free                                                            | Volume-weighting layer. [ec.europa.eu/eurostat](https://ec.europa.eu/eurostat/web/transport/data/database)                                                                             |
| **FlightAware AeroAPI**           | Per-flight schedule vs actual times, REST                                                               | 2011→                                                         | Free personal tier; commercial from $100/mo                     | Optional gap-filler — decide after free-source EDA.                                                                                                                                    |
| **Flightradar24 API**             | Per-flight positions + status                                                                           | Plan-dependent                                                | Explorer $9/mo →                                                | Cheapest paid per-flight history at small scale.                                                                                                                                       |
| **aviationstack**                 | Flight status API                                                                                       | ~3 months rolling                                             | Free 100 req/mo                                                 | Forward-collection tool, not backtest.                                                                                                                                                 |
| **Cirium**                        | Gold-standard OTP per flight                                                                            | Deep                                                          | Enterprise $$$                                                  | Overkill here.                                                                                                                                                                         |

_(No EU equivalent of the US BTS public per-flight on-time database exists; CAA + Eurocontrol
R&D archive is the closest free combination.)_

**Recommended stack:** (1) CAA monthly CSVs 2019–2025 for route×month P(3h+); (2) Eurocontrol
R&D archive samples for time-of-day/rotation multipliers; (3) forward fare scraper +
paper-trade log for live validation.

## 7. Sources

- UK CAA punctuality statistics: https://www.caa.co.uk/data-and-analysis/uk-aviation-market/flight-punctuality/
- Eurocontrol CODA Digest Annual 2023 (PDF): https://www.eurocontrol.int/sites/default/files/2024-12/eurocontrol-coda-digest-annual-report-2023.pdf
- Eurocontrol CODA Annual 2024: https://www.eurocontrol.int/publication/all-causes-delays-air-transport-europe-annual-2024
- Cirium On-Time Performance Review 2024 (PDF): https://assets.fta.cirium.com/wp-content/uploads/2025/01/02050431/2024-OTP-Annual-Review_20250101-1.pdf
- PA/CAA 2023 analysis: https://www.enfieldindependent.co.uk/news/national/24384336.wizz-air-ranked-worst-airline-delays-despite-soaring-fares/
- Which? — flight delays analysis: https://www.which.co.uk/news/article/why-are-so-many-flights-delayed-ak7C41l03njC
- AeroTime — 218,000 EU flights 3h+/cancelled in 2024: https://www.aerotime.aero/articles/218000-eu-flight-disruptions-may-cost-airlines-over-e6-billion-in-compensation
- flightright European airline ranking 2025: https://flightrights.net/en/blog/airline-ranking/
- Forbes — evening delay analysis: https://www.forbes.com/sites/garystoller/2019/06/03/most-flight-delays-in-the-evening-and-unrelated-to-bad-weather/
- Thrifty Traveler — first-flight-of-day analysis: https://thriftytraveler.com/guides/flights/data-analysis-first-flight-of-the-day/
- DLR low-cost fare survey via Daily News Hungary: https://dailynewshungary.com/wizz-air-overtakes-ryanair-as-europes-cheapest-low-cost-airline/
- Eurocontrol R&D Data Archive: https://www.eurocontrol.int/dashboard/aviation-data-research
- OpenSky Network data: https://opensky-network.org/data
- EU261 reference: https://en.wikipedia.org/wiki/Air_Passengers_Rights_Regulation
