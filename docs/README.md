# EU261 Delay-Compensation Arbitrage — Research Overview

**Question:** EU261/2004 pays a fixed €250–600 (UK261: £220–520) when a flight arrives ≥ 3
hours late for a non-exempt reason, regardless of ticket price. Budget carriers sell €15–40
fares and are widely reported to have Europe's worst delay records. Can you systematically buy
delay-prone cheap tickets and harvest the compensation?

**Status: OPEN — Phase 1 (data) running, first real base rates computed.** The research memos
below establish the legal framework (which is solid research) and a set of *hypotheses* about
the economics. The EV figures and feasibility conclusions are **not yet validated**; the first
measured numbers — P(3h+) by airline/route/month from raw CAA CSVs, 2019–2025 — are in
[`reports/base-rates.md`](../reports/base-rates.md) (`make all` reproduces them). Notably, the
real 2025 data shows Wizz Air's July P(3h+) at **0.90%** vs **3.41%** in July 2024 — the
best-cell rates the strategy would target have collapsed.

| Doc                                                                                  | Contents                                                                                    | Status |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- | ------ |
| [01 — Legal framework](research/01-eu261-legal-framework.md)                         | Regulation, case law, eligibility, weather nuance (§4.3), claim mechanics, 2026 reform outcome | Legal research — reliable |
| [02 — Delay statistics & candidates](research/02-delay-statistics-and-candidates.md) | Data sources, screening design, structural delay drivers, hypotheses to test               | Hypotheses — pending data |
| [03 — Quantitative model](research/03-quantitative-model.md)                         | EV math, EVT tail modeling, rotation propagation, Kelly, backtest methodology               | Methodology — parameters are placeholders |
| [04 — Feasibility & limitations](research/04-feasibility-and-limitations.md)         | Risk register: legal, operational, and market constraints                                   | Constraints researched; economic magnitudes untested |

---

## What is established (legal research, not subject to empirical testing)

1. **You must physically fly.** Article 3(2) EU261 requires presenting for check-in, and the
   CJEU held in *Laudamotion v flightright* (C-474/22, 25 Jan 2024) that compensation redresses
   time-loss actually suffered: a passenger who checks in online but doesn't board gets
   nothing. The C-756/18 evidentiary presumption (no boarding pass needed) is rebuttable by
   the airline's gate-scan manifest. Every bet therefore costs a human several hours of travel,
   and claims legally belong to the passenger who flew.
2. **The payoff trigger is delay ≥ 3h at arrival (doors-open, C-452/13) AND a non-exempt
   cause AND actually collecting.** Extraordinary circumstances (Art. 5(3)) exempt the airline
   from compensation; weather is an affirmative defence the airline must prove per flight, not
   a category (doc 01 §4.3).
3. **The 2026 reform kept the 3-hour threshold and the €250/400/600 amounts.** The June 2026
   Parliament–Council agreement rejected the Council's 4h/6h proposal; a 30-day payment
   deadline is incoming (~2027, pending plenary approval and the final
   extraordinary-circumstances annex).

## What is hypothesized (must be measured before it is believed)

- **Breakeven arithmetic** (this is just algebra): a €25 ticket against €250 needs
  P(collected) > 10% frictionless; claim friction (agency cuts, rejections, time) raises the
  hurdle. Whether any bookable cell (airline × route × time × season) clears it is the
  empirical question.
- **H1:** ULCC delay tails vary by an order of magnitude across cells; the worst
  route × month × rotation cells materially exceed carrier averages.
- **H2:** The correlated delay tail (ATC strikes, storms, ATFM) is largely exempt, so
  historical delay frequency overstates *claimable* probability most in exactly the cells that
  screen best (adverse selection). Plausible — but the eligibility share of 3h+ delays has no
  published statistic and must be estimated from cause data.
- **H3:** After eligibility and collection haircuts, no cell clears breakeven at realistic
  fares — i.e., the strategy is negative-EV. This is the prior suggested by market structure
  (claim agencies service organic delays rather than manufacture exposure; insurers price
  delay cover far below €250), but it is **unproven either way** until the pipeline runs.
- **H4:** Missed connections on single bookings (full-itinerary distance band per *Folkerts*)
  are the one channel that could materially change the EV geometry — scoped in doc 03 §1.4 and
  PLAN §6.

## What survives regardless of the verdict

1. **The free overlay:** if you're flying anyway and indifferent between departures, picking
   the statistically delay-prone one costs nothing and collects the same €250 when it hits.
2. **The pricing machinery:** a calibrated P(3h+ | booking-time info) model is directly the
   pricing engine for parametric delay insurance or claim purchasing — real businesses.
3. **The CV artifact:** a full quant research lifecycle landing on a disciplined, honest
   answer — whatever the data says. See [PLAN.md](PLAN.md) for the build-out.
