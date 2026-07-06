# Phase 5 — EV engine applied to the Phase 2 shortlist

Year 2025. 3,474 (cell x collection-path x wage-scenario) combinations evaluated from 579 shortlisted cells. Full table: `ev_ranked.csv`.

**Central result:** **no (cell x collection x wage) combination clears breakeven — EV ≤ 0 everywhere evaluated.**

## Best combination found

- Ryanair STANSTED→BERLIN BRANDENBURG, month 02
- P(3h+) = 2.95%, p_eligible = 42.3%, p_claimable = 0.998%
- Collection: diy, wage £0/h
- K_net = £220, all-in cost = £30.30
- **EV = £-26.70** per bet (breakeven p_claimable = 13.773%)
- Kelly fraction f = 0.0000

## Monte Carlo portfolio (best combination, 250 bets, 2000 sims)

- Mean season P&L: £-6554.96 (std £392.97, Sharpe -16.680)
- 95% CI: [£-7211.40, £-5701.14]
- Mean max drawdown: £6547.88
- Hit rate (bets that actually pay out): 1.163%
- Same-day clustering: gross delay correlation 0.016 vs. eligibility-filtered (claimable) correlation -0.002 — independent per-flight eligibility draws attenuate the clustered tail, as doc 04 §7 argues.

## Top 25 combinations by EV

| Carrier | Route | Month | Collection | Wage £/h | P(3h+) | p_claimable | K_net £ | Cost £ | EV £ | Kelly f |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ryanair | STANSTED→BERLIN BRANDENBURG | 02 | diy | 0 | 2.95% | 0.998% | 220 | 30.30 | -26.70 | 0.0000 |
| Ryanair | MANCHESTER→DUBLIN | 01 | diy | 0 | 2.84% | 0.886% | 220 | 30.30 | -26.93 | 0.0000 |
| Ryanair | STANSTED→BERLIN BRANDENBURG | 02 | agency | 0 | 2.95% | 1.123% | 143 | 30.30 | -27.26 | 0.0000 |
| Ryanair | MANCHESTER→DUBLIN | 01 | agency | 0 | 2.84% | 0.997% | 143 | 30.30 | -27.43 | 0.0000 |
| Ryanair | EDINBURGH→DUBLIN | 01 | diy | 0 | 1.70% | 0.596% | 220 | 30.30 | -27.54 | 0.0000 |
| Ryanair | STANSTED→DUBLIN | 01 | diy | 0 | 1.26% | 0.452% | 220 | 30.30 | -27.84 | 0.0000 |
| Ryanair | EDINBURGH→DUBLIN | 01 | agency | 0 | 1.70% | 0.670% | 143 | 30.30 | -27.87 | 0.0000 |
| Ryanair | LUTON→DUBLIN | 11 | diy | 0 | 0.99% | 0.348% | 220 | 30.30 | -28.06 | 0.0000 |
| Ryanair | LIVERPOOL (JOHN LENNON)→DUBLIN | 11 | diy | 0 | 0.88% | 0.333% | 220 | 30.30 | -28.09 | 0.0000 |
| Ryanair | STANSTED→DUBLIN | 01 | agency | 0 | 1.26% | 0.508% | 143 | 30.30 | -28.09 | 0.0000 |
| Ryanair | BIRMINGHAM→DUBLIN | 02 | diy | 0 | 0.77% | 0.287% | 220 | 30.30 | -28.19 | 0.0000 |
| Ryanair | STANSTED→DUBLIN | 11 | diy | 0 | 0.78% | 0.287% | 220 | 30.30 | -28.19 | 0.0000 |
| Ryanair | STANSTED→BERGAMO | 01 | diy | 0 | 0.85% | 0.285% | 220 | 30.30 | -28.19 | 0.0000 |
| Ryanair | BIRMINGHAM→DUBLIN | 01 | diy | 0 | 0.71% | 0.255% | 220 | 30.30 | -28.25 | 0.0000 |
| Ryanair | LUTON→DUBLIN | 11 | agency | 0 | 0.99% | 0.392% | 143 | 30.30 | -28.25 | 0.0000 |
| Ryanair | LIVERPOOL (JOHN LENNON)→DUBLIN | 11 | agency | 0 | 0.88% | 0.375% | 143 | 30.30 | -28.28 | 0.0000 |
| Ryanair | BIRMINGHAM→DUBLIN | 02 | agency | 0 | 0.77% | 0.323% | 143 | 30.30 | -28.35 | 0.0000 |
| Ryanair | STANSTED→DUBLIN | 11 | agency | 0 | 0.78% | 0.323% | 143 | 30.30 | -28.35 | 0.0000 |
| Ryanair | STANSTED→BERGAMO | 01 | agency | 0 | 0.85% | 0.320% | 143 | 30.30 | -28.35 | 0.0000 |
| Ryanair | BIRMINGHAM→DUBLIN | 01 | agency | 0 | 0.71% | 0.287% | 143 | 30.30 | -28.39 | 0.0000 |
| Ryanair | BIRMINGHAM→DUBLIN | 11 | diy | 0 | 0.00% | 0.000% | 220 | 30.30 | -28.79 | 0.0000 |
| Ryanair | BIRMINGHAM→DUBLIN | 11 | agency | 0 | 0.00% | 0.000% | 143 | 30.30 | -28.79 | 0.0000 |
| Ryanair | EDINBURGH→DUBLIN | 02 | diy | 0 | 0.00% | 0.000% | 220 | 30.30 | -28.79 | 0.0000 |
| Ryanair | EDINBURGH→DUBLIN | 02 | agency | 0 | 0.00% | 0.000% | 143 | 30.30 | -28.79 | 0.0000 |
| Ryanair | EDINBURGH→DUBLIN | 11 | diy | 0 | 0.00% | 0.000% | 220 | 30.30 | -28.79 | 0.0000 |

**Not priced (see `ev/engine.py` docstring):** missed-connection uplift, cancellation/re-routing legs, duty-of-care in-kind value — all require single-booking itinerary or per-flight cause data this pipeline never ingested. Only the pure-function band-edge screen (378 of 3,474 rows flagged within 150km of a compensation breakpoint) is included.
