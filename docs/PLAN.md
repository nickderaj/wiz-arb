# PLAN — EU261 Delay-Compensation "Arbitrage" Research Project

**Working title:** _Pricing the Lottery Ticket in Every Budget Airline Fare: A Quantitative
Analysis of EU261 Delay-Compensation Expected Value_

**Status:** All phases (1-7) built and run against real data — see per-phase status notes
below and `reports/*.md` for outputs. Headline result: **EV ≤ 0 in every evaluated
combination** (Phase 5/6); the market-structure prior (§8) held up under measurement,
not just assertion. Phase 1's fare panel remains an assumption model (no historical fare
archive exists — see §2 item 6); Phase 2's GPD/rotation-index items remain deferred
(flight-level data was never ingested — see §3). Write-up: `reports/paper.md` (Phase 7).

**Framing for the CV / quant interviews:** the deliverable is _not_ "a money-making strategy"
— it is a professional demonstration of the full quant research lifecycle applied to an
unconventional asset: hypothesis → legal/market microstructure research → data engineering →
tail-risk modeling → calibrated probability forecasting → EV/Kelly analysis → point-in-time
backtest → honest conclusion, whichever way the data lands. The market-structure prior (§8)
is that EV < 0, but that is a hypothesis to test, not a result. A rigorous, well-supported
"no-trade" conclusion is itself a strong signal of research discipline — but only if actually
earned from data.

---

## 0. The thesis in one paragraph

EU261/2004 pays a fixed €250/€400/€600 (UK261: £220/£350/£520) per passenger when a flight
arrives ≥ 3 hours late for a non-"extraordinary" reason — independent of ticket price. Budget
carriers (Wizz Air, Ryanair, easyJet, Vueling…) sell fares of €15–40 and have the worst delay
records in Europe. A €20 ticket with a €250 contingent payout is a 12.5× lottery ticket: the
bet is +EV iff P(compensable 3h+ delay) > c/K ≈ 8%. The project measures whether any bookable
cell (airline × route × time × season) clears that hurdle after eligibility filtering, claim
friction, and the cost of actually having to fly (which the law requires — CJEU C-474/22).

## 1. Repository layout (target)

```
wiz-arb/
├── docs/
│   ├── PLAN.md                    ← this file
│   ├── README.md                  ← executive summary of findings
│   └── research/
│       ├── 01-eu261-legal-framework.md
│       ├── 02-delay-statistics-and-candidates.md
│       ├── 03-quantitative-model.md
│       └── 04-feasibility-and-limitations.md
├── data/
│   ├── raw/                       # immutable downloads (CAA CSVs, CODA digests…)
│   ├── interim/                   # cleaned, typed parquet
│   └── processed/                 # feature matrices, point-in-time panels
├── src/wizarb/
│   ├── ingest/                    # per-source downloaders & parsers
│   ├── features/                  # booking-time feature engineering
│   ├── models/                    # P(delay≥3h) classifiers + calibration
│   ├── eligibility/               # extraordinary-circumstances / cause model
│   ├── ev/                        # EV engine, breakeven, Kelly, portfolio sim
│   └── backtest/                  # walk-forward harness, bootstrap CIs
├── notebooks/                     # numbered EDA/analysis notebooks
├── reports/                       # figures + final write-up (PDF)
└── tests/
```

Python 3.12, `uv` for env, pandas/polars, scikit-learn + LightGBM, statsmodels
(GPD/EVT via `scipy.stats.genpareto`), matplotlib. Everything reproducible via `make`.

## 2. Phase 1 — Data acquisition (the real bottleneck)

Priority order (free → paid):

1. **UK CAA punctuality statistics** (free, monthly CSVs, route × airline level: % on time,
   average delay, delay-band distributions incl. >180 min). Backbone of the backtest for
   UK-touching routes. Ingest 2016–present.
2. **EUROCONTROL CODA** digests (free PDFs/data): network-level delay causes (ATFM, weather,
   reactionary) → priors for the eligibility model.
3. **EUROCONTROL R&D data archive** (free for research, flight-by-flight ~4 datasets/yr):
   flight-level actual vs scheduled times for intra-European traffic.
4. **OpenSky Network** (free, research access): ADS-B derived movements to reconstruct
   aircraft rotations (tail-number level) → rotation-index and turnaround-slack features.
5. **Paid/optional top-ups:** FlightAware AeroAPI or Cirium for gap-filling and door-time
   proxies; aviationstack for spot checks. Budget cap: decide after free-source EDA.
6. **Fares:** no free historical fare archive exists → start a **forward-collecting scraper**
   (daily snapshot of Wizz/Ryanair/easyJet fares on the candidate routes produced by the
   Phase 2 screening) and accept that the historical backtest
   uses a conservative fare model (e.g., 25th-percentile advance-purchase fare by route/season).
   The fare model's bias is not neutral: fares and delay propensity are jointly driven by
   season/congestion, so a static fare model can create phantom edge in peak cells — report the
   backtest as a bound conditional on the fare model.
7. **Eurostat `avia_par_*`** (free): route-level passenger/flight volumes for volume-weighting
   candidate cells (down-weights thin routes that look attractive on % terms alone).

**Freshness requirement:** ingest **2025 CAA data alongside earlier years before modeling** —
Wizz Air's press-documented 2025 operational turnaround means 2024-only base rates would be
materially stale, and industry-wide schedule padding shifts the compensable tail independently.
OpenSky research access requires a justified application; frame it around the delay-modeling
research and treat refusal as a pipeline risk (fallback: Eurocontrol R&D archive only).

**Deliverable:** `data/interim/flights.parquet` — one row per flight leg: schedule, actuals,
delay minutes, carrier, route, aircraft rotation index; plus `fares.parquet` (forward panel).

## 3. Phase 2 — EDA & base rates

**Status: partially done.** The parts computable from CAA's route/airline/month *aggregate*
CSVs are implemented and run against real data (`src/wizarb/analysis/shortlist.py`,
`src/wizarb/features/distance_bands.py`; `make shortlist` → `reports/shortlist.md` +
`shortlist_<year>.csv`). The parts requiring flight-level records are **deferred, not
approximated** — see below.

- Done: empirical P(arrival delay ≥ 180 min) and P(cancel) by airline, airport, route, month
  (`analysis/base_rates.py`, already existed). Candidate shortlist per doc 02 §4: cells ranked
  by a gross screening ratio `(p_ge_3h × K) / assumed_fare`, using an approximate
  country-distance → UK261 compensation-band model, restricted to the carriers the fare model
  is calibrated for. **First real result: the max gross ratio across all 2025 cells is 0.71**
  (Wizz Air Luton→Tirana, May) — i.e. even before any eligibility haircut, collection haircut,
  or friction cost, no cell clears breakeven on this screening metric. Consistent with the
  market-structure prior (§8); to be revisited once eligibility (Phase 4) is layered on, since
  a screening ratio < 1 doesn't itself prove no cell can be positive-EV under different p_e/p_π
  assumptions than the implicit ones here (there are none yet — this ratio is gross, pre-haircut).
- **Not done / not attempted:** scheduled hour, rotation index — CAA aggregates carry no
  flight-level time-of-day or tail-number information.
- **Deferred, not approximated:** GPD tail fit above u = 60 min, decluster exceedances,
  cause-filtered tails, tail-index stability, and the last-rotation vs first-rotation delay
  multiplier all require flight-level data (Eurocontrol R&D archive / OpenSky, Phase 1 items
  3–4), which has not been ingested. Fitting a POT tail model on CAA's binned percentage columns
  would treat interval-censored aggregates as flight-level exceedances — doc 03 §2.2 explicitly
  flags this as invalid, so it was not attempted as a stopgap.
- Also not yet ingested: Eurostat `avia_par_*` route volumes (Phase 1 item 7) — the shortlist
  does not volume-weight/down-weight thin routes yet.
- **Deliverable:** `src/wizarb/analysis/shortlist.py`, `src/wizarb/features/distance_bands.py`,
  `reports/shortlist.md`. `notebooks/01-base-rates.ipynb` not created — output went to a report
  script instead; revisit if the write-up phase wants a notebook artifact.

## 4. Phase 3 — Probability model (the core ML artifact)

**Status: done, on the data actually ingested.** CAA's public CSVs are cell-level
(airport x destination x airline x month), not flight-level, so the per-flight binary
target below is reframed as a cell-month binomial rate (`n_ge_3h` of `n_flights`) — see
`src/wizarb/models/features.py` docstring for why this is a documented substitution, not
an approximation. Model ladder implemented: (a) two-level empirical-Bayes shrunken cell
mean, (b) weighted logistic regression, (c) `HistGradientBoostingClassifier` (LightGBM
substituted — this macOS/uv environment lacks the `libomp` runtime LightGBM's compiled
extension needs; see `models/ladder.py`). Walk-forward validated 2021–2025 with nested
isotonic calibration (`models/walkforward.py`, `wizarb model-backtest` →
`reports/model-backtest.md`). **Result: the shrunken baseline is a strong competitor** —
calibrated logistic/GBM beat it on 2025 Brier proxy only marginally (0.00038–0.00039 vs.
0.00039), i.e. most of the signal in this feature set is already captured by
hierarchical shrinkage; carrier + trailing rate dominate over month/route detail at this
data grain. `notebooks/02-model.ipynb` not created — output went to a report script,
consistent with Phase 2.

Binary target: `delay_arrival >= 180 min` (sensitivity band: **170–190 min** — 170 captures the
doors-open vs on-block measurement gap, _Germanwings_ C-452/13; 190 reflects airlines fighting
the boundary, so wins concentrated just over 3h are contested). **Not implemented**: the
170/190-min sensitivity band itself, since CAA's percentage columns are banded at 121–180 /
181–360 / >360 min, not at 170/190 — doing so would require flight-level data (same gap as
Phase 2's deferred GPD fit).

- **Constraint: booking-time information set only.** Cheap fares are bought 3–10 weeks out
  → no weather, no live rotation state. Features: carrier, route, airport congestion stats,
  scheduled hour, rotation index (**reconstructed from the published schedule alone** as of the
  simulated booking date — using realized tail assignments from historical ADS-B is look-ahead
  on the strongest covariate), turnaround slack, month/DOW, seasonal ATC strike calendar,
  trailing 12-month cell base rates (shrunken/hierarchical, keyed on **data-availability date**
  — CAA publishes ~2–3 months in arrears).
- Model ladder: (a) shrunken cell-mean baseline (hierarchical Bayes / empirical Bayes),
  (b) logistic regression, (c) LightGBM. The baseline must be beaten out-of-sample to justify
  complexity.
- **Calibration is the point, not ranking:** reliability diagrams, Brier score decomposition,
  isotonic/Platt recalibration **fit on a nested out-of-time fold inside the walk-forward
  loop** (never pooled future data). The trading rule is a _level_ threshold p̂ > p, so a
  well-calibrated 3% must mean 3%.
- **Deliverable:** `src/wizarb/models/` + `notebooks/02-model.ipynb`.

## 5. Phase 4 — Eligibility & collection haircuts

**Status: done, as a documented assumption model** (`src/wizarb/eligibility/`,
`wizarb eligibility` → `reports/eligibility.md`). No CODA cause-code ingest or METAR
storm-date matching exists (Phase 1 items 2/4 not built), so cause shares and
compensable fractions are anchored to doc 01/04's cited sources rather than fit —
flagged in the module docstring as the project's headline unvalidated sensitivity
axis, exactly as PLAN.md specifies. Resulting p_eligible: **43.6% winter, 38.1%
summer, 44.1% shoulder** at congestion_z=0 — inside the 0.35-0.55 band this section
anticipated, with summer (ATC/ATFM-heavy) eligibility below winter (weather-heavy) as
expected. Collection: DIY 80% paid / 6mo lag / full net; agency 90% paid / 3mo lag /
65% net (35% contingency cut) — both documented, not measured.

p_claimable = p̂_delay × p̂(non-extraordinary | delay) × p̂(paid | valid claim).

- Cause-code the delayed flights where possible (CODA cause shares; strike calendars; storm
  dates via METAR archives — allowed here because this is _outcome labeling_, not a
  booking-time feature).
- Key structural fact (doc 03/04): correlated mass-delay days (ATC, weather) are mostly
  **exempt**; claimable delays are idiosyncratic (technical/crew). Model eligibility share
  ~0.35–0.55 with segment variation — **flagged as unvalidated: no published statistic exists
  for the compensable share of 3h+ delays, so this is the headline sensitivity axis of the
  whole project**; payment success ~0.75–0.9 DIY (with months of latency) or ×(1−0.35) via
  agencies.
- **Weather is not a zero** (doc 01 §4.3): split weather-coded delays into exceptional
  (exempt) / ordinary + de-icing (substantially compensable — German BGH X ZR 146/23) /
  reactionary knock-on (contestable via the C-74/19 direct-causal-link and reasonable-measures
  limbs). Plausibly 20–40% of weather-tagged 3h+ delays are compensable; model p̂_e per cause
  bucket, decreasing in the same congestion covariates that increase p̂_delay. Check the
  **seasonal eligibility mix** too (winter skews weather/de-icing, summer skews ATC/ATFM).
- **Deliverable:** eligibility module + a documented haircut table with sources.

## 6. Phase 5 — EV engine, Kelly, portfolio simulation

**Status: done, and this is the project's first EV-level empirical result.**
`src/wizarb/ev/` (`engine.py`, `portfolio.py`, `report.py`); `wizarb ev` →
`reports/ev.md` + `ev_ranked.csv`. Swept the full 2025 shortlist (579 cells) x 2
collection paths x 3 wage scenarios (£0/12/25/h) = 3,474 combinations.
**Result: EV ≤ 0 in every combination evaluated** — the best (Ryanair
Stansted→Berlin Brandenburg, Feb, DIY, £0/h wage) is EV = **-£26.70/bet** against a
breakeven p_claimable of 13.8% vs. an actual 1.0%, roughly a 14x shortfall. This
confirms the market-structure prior (§8) at the EV level, not just the gross
screening-ratio level (Phase 2's 0.71 max). Monte Carlo on the best cell: mean
season P&L -£6,555/250 bets, Sharpe -16.7, 95% CI entirely negative. Correlation
diagnostic behaves as doc 04 §7 argues: gross delay same-day correlation ~0.02 vs.
claimable (eligibility-filtered) correlation ~0.00 — independent per-flight
eligibility draws attenuate the clustered tail. **Not priced** (documented in
`ev/engine.py`): missed-connection uplift, cancellation/re-routing legs,
duty-of-care value — all need itinerary/cause data this pipeline never ingested;
only the pure-function 1,500km band-edge screen is included (378/3,474 rows
flagged). Kelly fraction is 0 everywhere (no positive edge to size into).

- Per-flight EV: `EV = p_claimable × K_net − c − φ` (φ = claim friction + time cost at a
  parameterized wage; report at €0/h, €12/h, €25/h). Use **all-in c** (bag/seat/card fees add
  €10–20 over headline promo fares) and apply a **schedule-change kill probability** (~3–10%
  of months-ahead bookings lose their selected rotation to a re-timing/refund).
- Secondary payoff legs (doc 03 §1.4): cancellation <14d; carrier re-routing arriving ≥3h
  late; **missed connections on single bookings** (full-itinerary distance band per _Folkerts_
  — the one channel that materially changes the EV geometry; screen it explicitly);
  1,500 km **band-edge screening** (routes just over the boundary pay €400 at €250-band-like
  fares); duty-of-care in-kind value (survives extraordinary circumstances); multi-passenger
  amortization of φ.
- Breakeven frontier c vs p by compensation band; heatmaps of EV across cells.
- Kelly sizing f = (pK − c)/(K − c); portfolio of n flights: variance, Sharpe, day-blocked
  correlation (delays cluster but the clustered tail is exempt — show both gross and
  eligibility-filtered correlation).
- Monte Carlo P&L over a season with bootstrap confidence intervals.
- **Deliverable:** `src/wizarb/ev/` + `notebooks/03-ev-portfolio.ipynb`.

## 7. Phase 6 — Backtest

**Status: done.** `src/wizarb/backtest/walkforward.py`; `wizarb backtest` →
`reports/backtest.md` + `backtest_trades.csv`. Walk-forward 2022-2025, trading
signal = Phase 3's point-in-time shrunken baseline, settlement via Phase 4/5.
**At the true breakeven margin (trade iff predicted EV > £0), the backtest finds
zero trades in every year** — the correct behavior given Phase 5's cross-sectional
result, not a harness bug. A demonstration run at a relaxed margin (predicted EV >
-£21, chosen because the best predicted EV in the panel is ~-£20.2 — still a
losing "trade", never a recommendation) exercises the full mechanics: 2 trades,
total realized EV -£843, 95% bootstrap CI, max drawdown £421, ~4,680 seats/yr
capacity, mean annualized IRR -99.8%. Regulatory scenario panel: the enacted
2026 reform's 30-day payment deadline shortens DIY lag 6mo→1.5mo, which
*compresses* the already-negative annualized IRR further (a faster payout timeline
makes a no-edge trade's annualized loss rate look worse, not better — it cuts
friction, it doesn't create edge); the defeated Council 6h-threshold stress case
(the only exactly CAA-measurable leg of that proposal — 4h has no exact band) is
uniformly worse on the same trades, as expected.

- Walk-forward: train on years t−3…t−1, "trade" year t (2019 excluded-COVID discussion;
  2022 disruption summer as stress case).
- Point-in-time discipline: features frozen at simulated booking date (T−28d default);
  fares from the conservative fare model (documented as a limitation) until the forward
  scraper panel matures.
- Strategy: each day, rank bookable flights by p̂; "buy" those with p̂ > p + margin; settle
  with actual outcome × eligibility × collection haircut and latency (payout lag 2–12 mo, up to 24 litigated →
  IRR, not just total P&L).
- Report: cumulative P&L, hit rate, EV per bet with CIs, max drawdown, capacity (seats/yr
  clearing the threshold), and a regulatory scenario panel: the enacted 2026 reform (3h
  threshold and amounts **kept**; 30-day payment deadline reduces collection friction —
  doc 01 §8) as the base case, with the defeated Council 4h/6h thresholds retained as a
  historical stress case only.
- **Deliverable:** `src/wizarb/backtest/` + `reports/backtest.pdf`.

## 8. Phase 7 — Write-up (the CV artifact)

**Status: done.** `reports/paper.md` — three style variants (1 paragraph, 2-3
paragraphs, 1 page) of the same pipeline and result, plus a keyword-reference
section, in place of a single PDF (a markdown research note is more reviewable in
this repo and matches the rest of the project's markdown-report convention; the
content is written to the same 8-12-page research-note structure below and can be
rendered to PDF later without rewriting).

`reports/paper.pdf` (8–12 pages, quant-research-note style):
abstract → regulation & microstructure → data → tail model → calibration results →
EV/Kelly → backtest → **honest conclusion**. Hypotheses from the research phase, now
measured:

- Breakeven needs p ≈ 8–10% frictionless, **16–19% with realistic frictions** (algebra given
  the friction assumptions); the market-structure prior was that claimable p per cell falls an
  order of magnitude short — **confirmed**: best measured cell has p_claimable ≈ 1.0% against
  a ≈13.8% breakeven (Phase 5), roughly a 14x shortfall, not an order of magnitude off in the
  optimistic direction.
- Prior: the positive-EV set, if any, is small and concentrated in sub-€10 flash fares on
  1,500–3,500 km routes in idiosyncratic-delay cells. **Not confirmed or refuted** — the
  **missed-connection channel** (single-booking band uplift per _Folkerts_) remains unpriced
  (Phase 5: requires single-booking itinerary data this pipeline never ingested), so the
  "measure-zero" conclusion above is scoped to the priced legs only, per doc 03 §1.4's own
  caveat.
- Legitimate salvage value: (a) a _free overlay_ on travel you'd take anyway — pick the
  delay-prone departure when indifferent; (b) the pricing machinery transfers directly to
  claim-purchasing / parametric delay insurance, which **is** a real business (AirHelp) — and
  is exactly the calibrated-forecasting + EV-pricing + backtesting machinery this pipeline
  built (Phases 3, 5, 6).

## 9. Known constraints and risk register — summary

Full analysis in `research/04-feasibility-and-limitations.md`. Items 1 and 7 are established
legal facts; the rest are researched constraints whose _magnitudes_ are assumptions until the
pipeline measures what it can (eligibility share, rejection rates, and market pricing have
cited sources; the EV arithmetic built on them is untested):

1. **You must physically present for check-in and take the flight** (Art. 3(2); CJEU
   C-474/22, 25 Jan 2024). Online check-in + no-show pays nothing: airlines rebut the
   C-756/18 presumption with gate-scan manifests, the fare is forfeited, and no time-loss
   was suffered. Scaling therefore literally requires an army of travelling humans, whose
   wages exceed the edge.
2. Each bet consumes 4–10 hours of a human life; at plausible wage rates the time cost
   (€40–120) is expected to exceed gross EV — quantify with the parameterized-wage EV engine
   (§6) rather than assume.
3. The correlated delay tail (strikes, storms, ATC) is largely **exempt** as extraordinary
   circumstances — the portfolio's jackpot days pay €0. (Nuance: weather is an affirmative
   defence, not a category — 20–40% of weather-tagged delays are contestable, doc 01 §4.3 —
   which softens but does not reverse this.)
4. Airlines fight: ~half of valid claims initially rejected; Wizz Air alone had 2,500+ (Oct 2023)
   unpaid CCJs at peak; collection takes months-to-years or a 25–50% agency cut.
5. Market-structure prior against mispricing: EU261 costs (~€5/segment per industry studies)
   are embedded in fares, and AirHelp+ prices full disruption cover at ~€11–13/trip — the
   market's own EV estimate for the average trip mix. Bounds the average, not a cherry-picked
   cell; the pipeline tests the cells.
6. Systematic operation risks taxable-trade treatment (not automatic), the EU abuse-of-rights
   doctrine (cf. _Brillen Rottler_ C-526/24 on manufactured GDPR claims — an imperfect analogy
   since an EU261 bettor genuinely suffers the compensated harm), and carrier blacklisting.
7. Regulatory update: the June 2026 Parliament–Council agreement **kept the 3-hour threshold
   and €250/400/600 amounts** (the Council's 4h/6h proposal died); residual risk is plenary
   approval and the final extraordinary-circumstances annex. The 30-day payment deadline, if
   enacted (~2027), _reduces_ collection friction.

## 10. Milestones

| #   | Milestone                            | Est. effort |
| --- | ------------------------------------ | ----------- |
| M1  | CAA + CODA ingest, `flights.parquet` | 2–3 days    |
| M2  | Base-rate EDA + GPD tail fits        | 2 days      |
| M3  | Rotation reconstruction (OpenSky)    | 2–3 days    |
| M4  | Calibrated P(≥3h) model              | 3 days      |
| M5  | Eligibility haircuts + EV engine     | 2 days      |
| M6  | Walk-forward backtest + Monte Carlo  | 3 days      |
| M7  | Paper + repo polish                  | 2–3 days    |
