# Pricing the Lottery Ticket in Every Budget Airline Fare

### A Quantitative Research Note on EU261 Delay-Compensation Expected Value

Three write-ups of the same project, in increasing depth: a one-paragraph abstract, a
2-3 paragraph summary, and a one-page technical note. All three describe the same
pipeline and the same result — they are style variants for different audiences (CV
bullet / cover-letter paragraph / interview leave-behind), not different findings.
Full methodology and sources: `docs/PLAN.md` and `docs/research/01-04`. Full numeric
outputs: `reports/{shortlist,model-backtest,eligibility,ev,backtest}.md`.

---

## 1. One-paragraph version

Built an end-to-end quantitative research pipeline testing whether EU261/UK261
flight-delay compensation (a fixed €250-600 payout triggered by a 3-hour-plus arrival
delay) is mispriced relative to budget-carrier ticket prices — treating each cheap
fare as a lottery ticket and asking whether its expected value is positive. The
pipeline ingests seven years of UK CAA punctuality data, engineers point-in-time,
booking-horizon features with two-level empirical-Bayes hierarchical shrinkage,
validates a model ladder (shrunken cell-mean baseline vs. weighted logistic
regression vs. gradient-boosted trees) via walk-forward, out-of-time validation with
nested isotonic calibration (scored on weighted Brier score and log loss), applies a
documented eligibility/collection haircut model (legal-cause decomposition, claim
friction, payout latency), and prices each candidate route/airline/month cell through
an expected-value engine with Kelly-criterion position sizing, Monte Carlo portfolio
simulation, and a walk-forward trading backtest with bootstrapped confidence
intervals and a regulatory-scenario sensitivity panel. Result: expected value is
negative in every one of 3,474 evaluated (cell × collection-path × wage-scenario)
combinations — the best cell clears only ~7% of its breakeven claim probability — so
the backtest correctly executes zero trades at any true breakeven threshold. The
deliverable is the rigor of the research lifecycle (hypothesis → data engineering →
calibrated forecasting → EV/Kelly analysis → backtest → honest null result), not a
trading strategy.

---

## 2. Two-to-three paragraph version

**The question.** EU Regulation 261/2004 pays a fixed €250/400/600 (UK261:
£220/350/520) per passenger for a 3-hour-plus arrival delay, independent of ticket
price. Budget carriers sell €15-40 fares and have Europe's worst punctuality records,
so a cheap ticket with a fixed contingent payout resembles a leveraged lottery ticket:
positive expected value (EV) requires only P(compensable 3h+ delay) to exceed
roughly 8-19% of the fare-to-payout ratio (frictionless vs. realistic-friction
breakeven). This project builds the full quantitative research pipeline to test that
hypothesis empirically rather than assert it, and reports the result honestly in
either direction.

**The pipeline.** Data engineering ingests seven years (2019-2025) of UK CAA
punctuality statistics into a reproducible flight-cell panel. Feature engineering
respects point-in-time discipline throughout: every predictive feature is built from
a rolling trailing window with an explicit publication-lag offset, so no feature ever
touches same-period or future information relative to a simulated booking date. The
probability model is a ladder of increasing complexity — a two-level empirical-Bayes
/ hierarchical-Bayes shrunken cell-mean baseline, a weighted logistic regression
(GLM), and a histogram-based gradient-boosted classifier — evaluated by walk-forward,
out-of-time cross-validation with **nested isotonic calibration** fit only on prior
folds, and scored on a weighted **Brier score** decomposition and log loss with
**reliability diagrams**. The baseline turned out to be a near-undominated
predictor, with the more complex models beating it only marginally out-of-sample — a
result worth reporting on its own as a lesson in not over-engineering a forecasting
system. A documented eligibility model (grounded in EU case law: *Wallentin-Hermann*,
*Krüsemann*, the *extraordinary-circumstances* exemption) decomposes delay causes into
compensable and exempt shares by season, and a collection-friction model prices
claim-rejection and payout-latency risk (DIY vs. claims-agency paths). These feed an
**EV engine** that computes per-bet expected value, **Kelly-criterion** sizing, a
breakeven frontier, and a **Monte Carlo** portfolio simulation with **bootstrap
confidence intervals**, correlation-clustering diagnostics, and drawdown statistics.
A final **walk-forward backtest** — the standard quant-research validation
discipline — trades the model's live, point-in-time predictions against realized
outcomes across 2022-2025, with a regulatory-scenario sensitivity panel (the enacted
2026 EU261 reform vs. a historical counterfactual stress case) and an **IRR**
treatment of payout latency.

**The result.** EV is negative across every one of 3,474 evaluated combinations of
cell, collection path, and time-cost assumption; the single best cell (a Ryanair
route) shows an actual compensable-delay probability of ~1.0% against a breakeven
requirement of ~13.8% — roughly a 14x shortfall — and Kelly sizing is uniformly zero
(no positive edge to size into). The walk-forward backtest, run honestly at the true
breakeven threshold, therefore executes zero trades in every trading year, which is
the *correct* behavior of a properly built backtest applied to a strategy with no
measured edge, not a limitation of the harness. This confirms, at the EV level rather
than just the gross-screening level, the project's initial market-structure
hypothesis: EU261 risk is already priced into the market (via claim-firm insurance
products and embedded regulatory cost) and no bookable corner of it is exploitable by
a retail bettor. The value delivered is the research infrastructure and its honest
null result, and the same machinery (calibrated tail-probability forecasting,
EV/Kelly pricing, point-in-time backtesting) is the direct analogue of pricing
parametric delay insurance or any other contingent-claim product.

---

## 3. One-page version

### Motivation and hypothesis

EU261/2004 (and its UK analogue, UK261) fixes compensation at €250/€400/€600
(£220/£350/£520) for a 3-hour-plus arrival delay, regardless of the fare paid.
Budget carriers routinely sell €15-40 fares while posting the continent's worst
delay statistics. Framed as a contingent claim, a cheap ticket is a call option on a
fixed payout: it clears breakeven whenever P(compensable delay) exceeds
`cost / net_payout`, an algebraic threshold of roughly 8% frictionless and 16-19%
once realistic claim friction and time cost are included. This project's deliverable
is not "a trading strategy" but a demonstration of the complete quantitative research
lifecycle — hypothesis, legal/market-microstructure research, data engineering,
calibrated probability forecasting, contingent-claim pricing, and an honestly
reported backtest — applied to an unconventional but well-defined asset.

### Data and feature engineering

The data backbone is seven years (2019-2025) of UK CAA punctuality statistics, the
finest publicly available grain (carrier × airport × destination × month cell
counts, not individual flight legs — a data-reality constraint documented and
worked around rather than silently approximated). Feature engineering enforces
**point-in-time discipline** throughout: every trailing statistic is computed over a
rolling window offset by the CAA's real publication lag, so no feature used to score
a test period ever touches same-period or future data — the single most common
integrity failure in naive backtests.

### Probability model and calibration

The target — P(arrival delay ≥ 180 min) — is modeled with a three-rung ladder: (i) a
**two-level empirical-Bayes / hierarchical-Bayes shrunken cell-mean baseline**
(shrinking a route's rate toward its carrier's rate toward the global rate, weighted
by an exposure-based credibility factor); (ii) a **weighted logistic regression
(GLM)**; (iii) a **histogram-based gradient-boosted classifier**. All three are
evaluated with a **walk-forward, out-of-time validation** loop and **nested isotonic
regression calibration** fit exclusively on a held-out prior fold — never on pooled
future data — and scored via a weighted **Brier score decomposition**, **log loss**,
and **reliability diagrams**. Empirically, the shrunken baseline is a strong,
near-undominated predictor; the more complex models deliver only a marginal
out-of-sample improvement, a materially useful negative result about model
complexity in a low-signal, highly aggregated regime.

### Eligibility, collection, and EV/Kelly pricing

A documented (not fitted — flagged explicitly as the project's headline sensitivity
axis) eligibility model decomposes delay causes into technical/crew, weather,
ATC/ATFM, and other buckets by season, anchored to case law (*Wallentin-Hermann*,
*Krüsemann*) and EUROCONTROL cause-share priors, yielding a **p(non-extraordinary |
delay)** in the 38-44% range. A collection-friction model prices claim-rejection
risk and **payout latency** (DIY vs. claims-agency paths, 3-6 month lag, 0-35%
contingency cut). These combine into a full **expected-value (EV) engine**:
`EV = p_claimable × K_net − cost − time_cost`, with a **Kelly-criterion** sizing rule,
a breakeven frontier, and a **Monte Carlo simulation** of portfolio P&L with
**bootstrap confidence intervals**, **Sharpe ratio**, maximum drawdown, and a
same-day correlation-clustering diagnostic (showing that eligibility filtering
attenuates the correlated mass-delay tail, consistent with the legal structure).

### Backtest and result

A **walk-forward trading backtest** (2022-2025) trades the model's live,
point-in-time predictions against realized outcomes, with an **IRR** treatment of
payout latency and a regulatory-scenario panel (the enacted 2026 EU261 reform vs. a
historical stress-case counterfactual). **Result: EV ≤ 0 in all 3,474 evaluated
(cell × collection-path × wage-scenario) combinations**; the best cell's actual
claimable-delay probability (~1.0%) falls roughly 14x short of its breakeven
(~13.8%); Kelly sizing is uniformly zero; and the backtest, run honestly at the true
breakeven margin, correctly executes zero trades in every year — the expected
behavior of a rigorous backtest applied to a strategy with no measured edge. This
confirms the project's initial market-structure hypothesis at the EV level, not just
the screening level: EU261 risk is already priced into fares and into third-party
disruption-insurance products, and no bookable corner of it clears breakeven for a
retail bettor. **A rigorous, well-supported "no-trade" conclusion, honestly earned
from real data rather than assumed, is itself the point of the exercise** — and the
same infrastructure (calibrated tail-probability forecasting, contingent-claim EV
pricing, point-in-time backtesting) is directly transferable to pricing parametric
delay insurance or any other fixed-payout contingent claim.

---

## Key techniques and terminology (for reference)

Expected value (EV) modeling · Kelly criterion / optimal position sizing ·
point-in-time / booking-time feature engineering · empirical Bayes / hierarchical
Bayes shrinkage · generalized linear models (weighted logistic regression) ·
gradient-boosted trees (histogram-based) · walk-forward / out-of-time
cross-validation · nested calibration · isotonic regression · Platt scaling ·
Brier score decomposition · log loss · reliability diagrams · binomial /
exposure-weighted regression · Monte Carlo simulation · bootstrap confidence
intervals · Sharpe ratio · maximum drawdown · internal rate of return (IRR) ·
tail-risk / extraordinary-circumstances decomposition · scenario / sensitivity
analysis · reproducible data pipelines.
