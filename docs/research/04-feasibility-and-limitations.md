# 04 — Feasibility and Limitations: Risk Register

**Role of this document:** Devil's advocate. Documents 01–03 set out the legal framework and
the EV methodology (with placeholder parameters — nothing measured yet). This document
catalogues the practical constraints and risks the strategy faces when it touches the real
world, independent of the EV math. The _legal_ constraints (§1, §5) are established research;
the _economic magnitudes_ quoted alongside them are assumptions or third-party figures until
the pipeline measures what it can.

**Framing up front:** even before any data work, the structure is clear — the compensation
leg is contingent on physically flying, on the airline paying (documented to require a fight),
and on the delay cause not being exempt. Whether these frictions leave any positive-EV corner
is the open empirical question the pipeline (PLAN.md) exists to answer.

---

## 1. The physical presence requirement (the strategy-killer)

### 1.1 What the law actually requires

EU Regulation 261/2004 **Article 3(2)(a)** conditions the whole regulation on the passenger
having "a confirmed reservation on the flight concerned and, except in the case of cancellation
referred to in Article 5, **present themselves for check-in** … as stipulated and at the time
indicated in advance … or, if no time is indicated, **not later than 45 minutes before the
published departure time**."

Key points:

- **For delay compensation you must present yourself for check-in and take the flight.** The
  Sturgeon line of case law that extends Article 7 compensation to 3h+ delays is built on
  passengers who _suffered_ the delay — i.e., who arrived at their final destination 3+ hours
  late. A person who checks in online and stays home does not arrive late; they simply don't
  travel. There is no delay damage to compensate.
- **CJEU Case C-756/18 (LC and MD v easyJet, order of 24 Oct 2019)** softened the _evidentiary_
  burden, not the _substantive_ requirement. The Court held that passengers with a confirmed
  reservation on a 3h+ delayed flight **cannot be denied compensation solely because they cannot
  produce a boarding card as proof of presence at check-in** — _"unless it can be established
  that those passengers were not transported on the delayed flight at issue."_ In other words:
  confirmed reservation ⇒ rebuttable presumption you were on board; the airline can rebut it
  with its own records.
- **The rebuttal is trivial for the airline.** Airlines hold the departure control system (DCS)
  records: boarding-pass scans at the gate, passenger manifests, APIS data. A no-show is flagged
  automatically (your seat is released, your return legs are typically cancelled under no-show
  clauses). For a systematic claimant, the airline will simply pull the gate-scan log and prove
  non-transport. C-756/18 protects the honest passenger who lost their paper boarding pass; it
  does **not** create a check-in-online-and-stay-home loophole.
- **Online check-in alone is therefore insufficient.** It may satisfy the _formal_ Article 3(2)
  condition, but if you were not transported on the delayed flight you were not delayed, and the
  airline's manifest proves it. No-show = fare forfeited, no compensation, and (on low-cost
  carriers) cancellation of any remaining segments.

### 1.2 The time-cost arithmetic

If you must actually fly, each "bet" costs:

| Component                                                        | Time       |
| ---------------------------------------------------------------- | ---------- |
| Travel to departure airport + security + 45-min check-in cutoff  | 2–3 h      |
| Flight (intra-EU short haul)                                     | 1–3 h      |
| The delay itself when you "win" (3h+ by definition, often 4–6 h) | 0–6 h      |
| Arrival processing + getting somewhere useful at destination     | 1 h        |
| **Total per bet (no return)**                                    | **4–10 h** |

- At even a €10–12/h opportunity cost (roughly EU minimum-wage territory), that is **€40–120 of
  labor per bet** — before the ticket price, before ground transport, before the return flight.
  (Someone with flexible dead time — a student working on a laptop in the departure lounge —
  loses less than wage-rate hours; doc 03's parameterized-wage approach, reporting EV at €0/12/25
  per hour, is the right treatment. Even at €0/h the EV stays negative on ticket cost alone.)
- If the per-bet gross EV is (P(compensable 3h+ delay) × €250) − ticket cost, then even under
  an optimistic _assumed_ delay pick of P ≈ 5–10% (unmeasured — the published EU-wide base
  rate for 3h+/cancelled is ~1.5%), gross EV would be **€12–25 per bet minus a €20–40
  ticket** — near zero or negative _before_ labor. Whether any real cell supports even that P
  is for the pipeline to establish.
- **Throughput ceiling:** one person can realistically execute at most ~2 bets/day (an outbound
  and a return), and every outbound strands you in a random European city, so the "second bet"
  is forced to be the return leg — whose delay probability you did not get to optimize.

**Structural takeaway:** the physical presence requirement converts a "financial bet" into
hours of mandatory labor per attempt; the EV engine must price that labor explicitly
(parameterized wage, doc 03 §4.4) rather than ignore it.

## 2. Scale problems

- **The return-leg tax.** Every bet physically relocates you. Either you buy a return (doubling
  cost c, and the return is rarely on your delay-optimized shortlist) or you overnight in the
  destination (hotel + time). This roughly doubles the denominator of the EV calculation.
- **No parallelization without payroll.** The claim belongs to the passenger who flew. To run N
  simultaneous bets you need N warm bodies with matching ID (airlines name-match at the gate
  against passports). Paying gig workers even €50–80/day plus tickets erases the entire spread;
  and workers would have a direct incentive to keep the compensation (it is legally _theirs_ —
  they are the passenger; you'd need assignment-of-claim contracts, which airlines like Ryanair
  contest and which add legal overhead per claim).
- **No evidence anyone runs a "professional passenger" farm.** Extensive searching finds no
  documented gig-economy scheme of paid passengers farming EU261 delays. What _does_ exist at
  industrial scale is the **claims-management industry** (AirHelp, Flightright, Skycop, bott &
  co) — firms that monetize _other people's_ organic delays for a 25–50% cut. This is the
  market's revealed answer: the only scalable business here is servicing claims, not
  manufacturing exposure. If buying tickets on delay-prone flights were +EV, the claim firms —
  who have the best delay data in the world — would be doing it. They aren't.
- **Selection against you at scale.** Repeat bookings by the same names on chronically delayed
  rotations are exactly the pattern airline revenue-integrity/fraud teams are built to flag
  (they already police hidden-city ticketing, duplicate bookings, and chargeback abuse).

## 3. Airline countermeasures

- **Default posture is denial.** AirHelp's 2024 caseload analysis found **~52% of valid UK
  claims were rejected at first response**, and over a quarter of claims were simply ignored;
  industry-wide estimates run to "up to 60% of airline rejections are of valid claims."
- **Wizz Air specifically** (the presumed counterparty in this project) has a documented
  enforcement record:
  - CAA analysis for the 12 months to March 2023: five airlines were ordered to pay **£11.46m**
    by courts/adjudicators; **Wizz Air alone accounted for ~£4.9m (over 40%)**.
  - Wizz Air had **1,601 outstanding County Court Judgments (>£2m) in March 2023, rising to
    2,587 by October 2023** — i.e., it was not paying even after _losing in court_.
  - The CAA forced Wizz Air to **re-review ~25,000 wrongly rejected claims** dating back to
    March 2022.
  - Wizz Air routinely attempts to pay in **"Wizz credits"** rather than cash; you can insist on
    cash (Article 7(3) requires cash/transfer unless the passenger agrees otherwise), but that
    is another round-trip of correspondence.
  - Ryanair has had aircraft **boarded by bailiffs** (Linz, 2026) to enforce an unpaid
    compensation judgment. That is the level of friction a _single_ claim can require.
- **Enforcement adds months-to-years and cost.** AviationADR/CEDR: airline has 28 days to
  respond + 28 days to pay if it settles; real-world reports range from ~2 months to **9+
  months**. Small-claims/county court: issue fees, hearing wait times (Which? reported cases
  taking years during backlog peaks), and even a won CCJ can sit "outstanding" (see Wizz above).
  A claims firm takes 25–50% of the payout to absorb this — which, applied to your €250, cuts
  the win to €125–188 and destroys marginal EV.
- **Blacklisting risk.** Ryanair has blacklisted ~850 passengers over chargebacks and its terms
  reserve broad rights to refuse carriage. There is no documented case of banning someone _for
  EU261 claims per se_, but a systematic claimant betting repeatedly against one or two low-cost
  carriers is exposed to exactly this discretionary weapon — and losing access to the cheap
  carrier ends the strategy.
- **No-show rules.** If you don't board: fare forfeited, no compensation, onward/return segments
  cancelled. If you _are_ denied boarding involuntarily you get compensation — but you cannot
  engineer that; showing up late to the gate is a no-show, not a denied boarding.

## 4. Selection effects: why the cheap fares aren't mispriced

- **Cheap fares are cheap because demand is low**, not because delay risk is unpriced: 6 a.m.
  departures (which are the _most_ punctual — first rotation of the day), late-night returns,
  midweek dates, secondary airports. The delay-prone slots (last rotation of the evening out of
  congested hubs in summer) are not systematically the cheapest — they're often peak-demand
  business/leisure return slots. (This is a testable hypothesis, not a fact — Phase 2 of the
  plan should measure the fare×delay-propensity correlation rather than assert it.)
- **Delay probability is only weakly predictable at booking time.** Academic ML work on
  flight-delay prediction (departure-delay distribution forecasting, spatio-temporal network
  models) gets useful signal only close to departure (rotation propagation, weather, ATC
  regulation); at booking horizon (days–weeks out), route/carrier/time-of-day base rates are the
  whole model, and those base rates for _compensable 3h+_ delays are low single digits.
- **EU261 costs are already in the fare.** The EU Commission puts the industry's EU261 cost at
  ~**€8bn/year** (with reform proposals pushing toward €15bn); ERA/A4E industry studies estimate
  the current per-passenger regulatory cost at roughly **€5 per segment** (against average
  airline profit of ~€7.80/passenger — IATA 2025), with older estimates in the €1–3 range.
  Spread across all tickets, the compensation pool is funded by ticket buyers collectively. You
  are not exploiting a mispricing; you are buying a lottery ticket whose premium is embedded in
  every fare, then paying extra (your time, your travel) for the privilege of collecting it.
- **The adverse-selection kicker:** any route where 3h+ delays were predictably frequent enough
  to make this +EV would be hemorrhaging money for the carrier (compensation often exceeds the
  fare several times over) — carriers eventually re-time, re-fleet, or cut such rotations. The
  opportunity tends to be self-extinguishing, though slowly: Wizz kept structurally bad
  rotations through 2022–24 until CAA intervention and its 2025 ops-investment turnaround, so
  persistence of bad cells is an empirical question, not an assumption in either direction.
- **Your counterparty is fixing the very dysfunction you'd be long.** The 2024-vintage base
  rates that make the best cells screen well were the product of Wizz's GTF-engine groundings
  and the 2022–24 ATC capacity crisis; Wizz's documented 2025 punctuality turnaround (OTP up
  ~14–22%) plus industry-wide schedule padding mean a model trained on the bad regime and
  traded in the improving one overstates live p by perhaps 1.3–2×.

## 5. Tax and legal

- **Tax.** One-off EU261 payments to consumers are treated as non-taxable compensation for
  inconvenience (UK: not declarable; interest on top is). Hobby-level claiming stays untaxed.
  The analysis _could_ flip for a systematic operation: under the UK "badges of trade" (and
  analogous EU member-state doctrines), systematic, profit-motivated, repeated transactions can
  be trading income — though the characterization is far from automatic (systematic gambling is
  famously non-trading in UK law), and tax on a negative-EV activity costs nothing in
  expectation. Treat this as a secondary risk for a scaled operation, not a primary argument.
- **Abuse of rights.** EU law has a general anti-abuse doctrine (two-pronged: formal compliance
  with a rule's conditions + failure to achieve the rule's purpose). The nearest modern
  authority is **_Brillen Rottler_ (C-526/24, 19 March 2026)**, where the CJEU held that
  systematically **manufacturing the conditions for a GDPR damages claim** (subscribing to
  newsletters to trigger access requests) can be refused as abusive and breaks the causal chain
  to compensable damage. The read-across to EU261 is real but weaker than it first looks: the
  GDPR hopper manufactures the _injury_; an EU261 bettor genuinely buys a ticket, genuinely
  flies, and genuinely loses 3+ hours — the "serious trouble and inconvenience" the regulation
  compensates is actually suffered, so a court would find abuse much harder to establish. It
  remains a tail risk for a discovery-exposed serial operator (dozens of one-way bookings to
  cities never left the airport of), not a ready-made defence template.
- **Also note Article 3(3):** passengers travelling free or on reduced fares "not available
  directly or indirectly to the public" are excluded — a farm using staff/industry discounts is
  outside the regulation entirely.

## 6. The insurance comparison: the market has already priced this

- **AirHelp+** sells the other side of this exact bet: Smart plan **€39.99/yr for 3 trips**
  (~€13/trip), Pro **€99.99/yr for 9 trips** (~€11/trip), including AirPayout parametric
  insurance (~€100 paid automatically on disruption) and fee-free claim handling.
- Read that as a market price: a firm with the world's best EU261 claims dataset prices
  full-service disruption coverage at **~€11–13 per trip**. If the expected harvestable
  compensation per deliberately chosen trip materially exceeded that, AirHelp's actuaries would
  be arbitraged by their own customers — and premiums would rise. The premium is an EV estimate
  for the _average organic trip mix_ (service costs and profit load included) — it bounds the
  average, not a cherry-picked cell, so it is directional evidence rather than a per-cell proof.
  Still an order of magnitude below €250.
- Claims firms' fee structure (25–50% contingency) tells the same story: the costly part is not
  finding delays, it's _collecting_.
- **Nobody has done this.** Searches for "professional passenger" schemes, EU261 delay-farming
  blogs, HN/Reddit write-ups of deliberate delay-betting find: claims-management guides,
  parametric flight-delay insurance startups (the CNBC-covered on-time-bet products — again,
  _selling insurance_, not buying delays), and nothing else. The closest documented behaviors
  are (a) claim firms monetizing organic delays and (b) airlines _manipulating arrival times_
  (taping doors shut to round a 2h57 delay under 3h — flight-delayed.com documented the reverse
  case) — i.e., the sophisticated players fight over marginal minutes on organic delays rather
  than manufacturing exposure. The dog that didn't bark is loud: a decade-plus of EU261, a whole
  industry of delay-data specialists, and zero delay-farming operations.

## 7. Operational frictions and the correlation problem

- **Payout latency:** direct claims commonly take 6–12 weeks when uncontested; contested claims
  via ADR run 2–9 months; court routes 6 months–2+ years (and Wizz Air's CCJ backlog shows even
  a judgment isn't cash). Your "bankroll" is locked in receivables with an uncertain haircut.
- **Initial rejection is the norm, not the exception:** ~half of valid claims rejected on first
  contact (AirHelp 2024 UK data); each rejection costs another cycle of escalation labor.
- **Cash vs vouchers:** Article 7(3) entitles you to cash, but Wizz Air's default push to "Wizz
  credits" means another fight per claim.
- **Extraordinary-circumstances disputes** are the airline's universal first move (weather, ATC,
  "hidden manufacturing defects"), and disproving them requires METAR/EUROCONTROL evidence the
  individual claimant rarely has.
- **The fat tail is stripped — the correlation problem.** Delay risk across flights is _not_
  independent: mass-delay days cluster on ATC strikes, ATC capacity regulations, storms, and
  airport closures. The CJEU treats **ATC strikes, airport/security staff strikes, severe
  weather, and air-traffic-management restrictions as "extraordinary circumstances"** — no cash
  compensation (only duty of care). Airline-internal causes (technical faults per
  _Wallentin-Hermann_, own-staff strikes per _Krüsemann_/C-28/20) pay. So exactly on the days
  when your portfolio of bets would pay off simultaneously (the tail you're betting on), most of
  the payouts are exempt. What remains compensable is the idiosyncratic, hard-to-predict,
  airline-internal delay — the part your booking-time model has the _least_ edge on. Europe's
  worsening delay picture (~3 in 10 flights >15 min late in 2023; ATC delays doubling over a
  decade per IATA) is dominated by ATC/weather causes, i.e., mostly the exempt kind.
  (Softening, not reversal: weather is an affirmative defence, not a category — ordinary
  weather/de-icing, remote knock-ons, and reasonable-measures failures make perhaps 20–40% of
  weather-tagged 3h+ delays contestable, see doc 01 §4.3. The correlated tail is _mostly_
  stripped, not entirely.)
- **Additional operational failure modes, briefly:**
  - _Schedule-change kill switch_: LCCs re-time/cancel thin routes >14 days out (~3–10% of
    months-ahead bookings) — the selected rotation position evaporates into a refund.
  - _Arrival-time shaving_: airlines fight the doors-open boundary (C-452/13); the effective
    threshold is ~185–190 min, thinning exactly the just-over-3h mass where wins concentrate.
  - _Scope-by-direction gaps_: parts of the Wizz network (e.g., Wizz Air Abu Dhabi sectors
    inbound to the EU) fall outside EU261/UK261 — a screener unaware of scope-by-direction
    overstates coverage.
  - _Financing droughts_: a 96%+ per-ticket loss rate crossed with 6-week-to-2-year payout
    latency means dozens of consecutive all-loss months before the first receivable clears —
    ruin dynamics at small bankrolls that EV-level Kelly analysis doesn't capture (doc 03 §4.6
    has the drought math).
  - _Pre-flight booking cancellation_: revenue-integrity systems can cancel suspicious
    duplicate/pattern bookings before travel — exposure begins before the first claim, not
    after it.

---

## Risk summary

1. **You must fly.** Article 3(2) + the manifest evidence standard of C-756/18 mean online
   check-in without boarding yields nothing: the airline proves non-transport from gate scans,
   the fare is forfeited under no-show rules, and there is no delay to compensate. This single
   fact converts every bet into a 4–10 hour physical commitment.
2. **Labor cost is expected to exceed gross EV.** €40–120 of time per bet against an
   _assumed_ €12–25 optimistic gross expected compensation minus a €20–40 ticket. To be
   quantified by the EV engine with measured probabilities and a parameterized wage.
3. **You can't scale it.** Claims are personal; parallelization requires paying passengers,
   which consumes the margin; returns double the cost; no such operation is documented anywhere,
   in an industry crawling with delay-data specialists who would have found it.
4. **The counterparty doesn't pay.** ~52% of valid claims initially rejected; Wizz Air's 2,500+
   outstanding CCJs and CAA-forced re-review of 25,000 claims show that _winning_ is a
   months-to-years collections problem, with 25–50% contingency fees or your own litigation
   labor as the collection cost.
5. **The tail is mostly exempt.** Correlated mass-delay days (ATC strikes, storms, ATFM
   regulations) are mostly "extraordinary circumstances" — the highest-payout scenarios pay €0
   (though 20–40% of weather-tagged delays are contestable via the ordinary-weather /
   causal-link / reasonable-measures routes, doc 01 §4.3). What reliably pays is idiosyncratic
   airline-internal delay, the least predictable component at booking time.
6. **Market structure argues against a mispricing.** EU261's ~€8bn/yr cost (~€5/passenger-
   segment, industry studies) is embedded in fares; AirHelp+ prices full disruption coverage at
   ~€11–13/trip, an order of magnitude below the €250 headline. These bound the _average_ trip,
   not a cherry-picked cell — the cell-level test is the pipeline's job.
7. **Legal and tax downside is asymmetric, if secondary.** Systematic operation risks
   taxable-trade treatment (not automatic), exposes the pattern to the EU abuse-of-rights
   doctrine (cf. _Brillen Rottler_ C-526/24 against GDPR claim-manufacturers — an imperfect
   analogy since an EU261 bettor genuinely suffers the compensated harm), and invites
   discretionary blacklisting by the very carriers whose cheap fares the strategy needs.

**Working hypothesis (untested): not an arbitrage.** The constraints above suggest negative
expected value after time costs for a solo operator, and worse at scale — but that is the
prior to be tested, not the finding. The empirical program in PLAN.md either overturns it in
some measurable corner (e.g., the missed-connection channel) or confirms it with numbers.

---

## Sources

### Law and cases

- Regulation (EC) No 261/2004, consolidated text — https://eur-lex.europa.eu/eli/reg/2004/261/oj/eng
- Commission Interpretative Guidelines on Reg. 261/2004 (2024) — https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:C_202405687
- CJEU Order C-756/18 (LC, MD v easyJet), summary — https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=oj:JOC_2020_045_R_0007
- European Commission, Summary of most relevant CJEU judgments on air passenger rights (2022) — https://transport.ec.europa.eu/system/files/2022-03/2022-summary-of-the-most-relevant-cjeu-judgements.pdf
- Ploum, "Boarding pass as a golden ticket: when does a passenger have a confirmed reservation?" — https://ploum.nl/en/news/boarding-pass-as-a-golden-ticket-when-does-a-passenger-have-a-confirmed-reservation
- Winglet Law, Reg. 261/2004 Article 3 commentary — https://wingletlaw.com/regulation-ec-261-2004-article-3/
- Your Europe — Air passenger rights (45-min check-in condition) — https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm
- CMS, "CJEU on the GDPR: Abuse of rights, causation and compensation" (C-526/24 Brillen Rottler) — https://cms.law/en/deu/legal-updates/cjeu-on-the-gdpr-abuse-of-rights-causation-and-compensation
- Greenberg Traurig, "CJEU: First Request for Access May Be Rejected as Abusive Under GDPR" — https://www.gtlaw.com/en/insights/2026/3/cjeu-first-request-for-access-may-be-rejected-as-abusive-under-gdpr
- Kluwer, "Abuse of EU Law Revisited" — https://kluwerlawonline.com/journalarticle/European+Public+Law/28.3/EURO2022017

### Airline behavior and enforcement

- CAA, "Regulator raises concerns with Wizz Air following complaints" — https://www.caa.co.uk/news/regulator-raises-concerns-with-wizz-air-following-complaints/
- Which?, "Airlines ordered to pay over £11m … Wizz Air responsible for over 40%" — https://www.which.co.uk/news/article/airlines-ordered-to-pay-over-11m-after-travel-chaos-with-wizz-air-responsible-for-over-40-aScRw7r2qyZq
- City A.M., "Wizz Air ordered to review years of falsely rejected compensation claims" — https://www.cityam.com/wizz-air-ordered-to-review-years-of-falsely-rejected-compensation-claims/
- Mighty Travels, "Wizz Air ordered to review 25,000 rejected claims" — https://www.mightytravels.com/2024/07/wizz-air-ordered-to-review-25000-rejected-compensation-claims-following-caa-intervention/
- TTG, "Wizz Air complaints handling and compensation delays 'unacceptable', says CAA" — https://www.ttgmedia.com/news/wizz-air-complaints-handling-and-compensation-delays-unacceptable-says-caa-37703
- Irish Times, "Bailiffs board Ryanair plane after airline refuses to pay compensation" (2026) — https://www.irishtimes.com/ireland/2026/03/13/bailiffs-board-ryanair-plane-after-airline-refuses-to-pay-compensation-to-passenger/
- Aerospace Global News, Ryanair bailiffs / Linz — https://aerospaceglobalnews.com/news/ryanair-bailiffs-unpaid-passenger-compensation-claim-linz-airport/
- Which?, "From blacklists to unfair fees: are airline terms unlawful?" (Ryanair chargeback blacklist) — https://www.which.co.uk/news/article/airline-compensation-refund-breaking-the-law-aiIty8R4mWLL
- AirHelp, "Why airlines reject valid flight compensation claims" — https://www.airhelp.com/en-int/blog/wrongful-claim-rejections/
- The Traveler, "Airlines wrongly reject over half of valid UK claims, AirHelp finds" — https://www.thetraveler.org/airlines-wrongly-reject-over-half-of-valid-uk-flight-compensation-claims-airhelp-finds/
- CAA, "What to do if your claim is rejected" — https://www.caa.co.uk/passengers-and-public/resolving-travel-problems/delays-and-cancellations/making-a-claim/what-to-do-if-your-claim-is-rejected/
- AviationADR — https://www.aviationadr.org.uk/
- Which?, "Compensation court cases could take years" — https://www.which.co.uk/news/article/more-airline-passenger-misery-as-court-cases-could-take-years-a0Cbv3r4ziOt
- Secret Claims, Wizz Air extraordinary-circumstances behavior — https://secretclaims.com/index_start.php?article=1-Wizzair-extraodrinary-eu261-Compensation-Request&lang=en

### Economics, pricing, and delay data

- ERA, "An ERA study into Regulation EU261" (2019) — https://www.eraa.org/wp-content/uploads/2025/12/ERA-Study-into-Regulation-EU261-2019.pdf
- Joint industry position, EU261 revision (cost per passenger estimates) — https://www.eraa.org/wp-content/uploads/2025/10/Joint-Industry-Position-EU261-revision_15102025.pdf
- Aerospace Global News, "EU261 reform: expanded rights could 'double' costs" (€8bn→€15bn; €5→€10/pax) — https://aerospaceglobalnews.com/news/eu261-reform-a4e-passenger-rights-airline-costs/
- EUROCONTROL, All-Causes Delays to Air Transport in Europe, Annual 2024 — https://www.eurocontrol.int/publication/all-causes-delays-air-transport-europe-annual-2024
- EUROCONTROL Data Snapshot #44, causes of flight delays — https://www.eurocontrol.int/publication/eurocontrol-data-snapshot-44-causes-flight-delays
- IATA, "European air traffic control delays double over last decade" — https://www.iata.org/en/pressroom/2025-releases/2025-12-09-03/
- ScienceDirect, "Dynamically forecasting airline departure delay probability distributions" — https://www.sciencedirect.com/science/article/pii/S0969699725000511
- TravelFreak, US airline delay statistics (budget-carrier punctuality) — https://travelfreak.com/airline-delay-statistics/

### Insurance/market prices and prior attempts

- AirHelp+ product page — https://www.airhelp.com/en/airhelp-plus/
- Travel-Dealz, AirHelp+ pricing breakdown — https://travel-dealz.com/deal/airhelp-plus/
- AirHelp fee schedule — https://www.airhelp.com/en/price-list/
- CNBC, "This guy is betting your flight will be on time" (parametric delay insurance) — https://www.cnbc.com/2014/11/26/this-guy-is-betting-your-flight-will-be-on-time.html
- Flight-Delayed.com, "Manipulating arrival time: airlines' trick to deny compensation" — https://www.flight-delayed.com/en/blog/2025/05/01/manipulating-arrival-time-airlines-trick-to-deny-compensation

### Strikes / extraordinary circumstances

- Flightright, "ATC strikes: your rights & compensation" — https://www.flightright.com/blog/atc-strikes-compensation
- Dudkowiak & Putyra, "EU261: strikes and armed conflicts" — https://www.dudkowiak.com/aviation-law-in-poland/eu261-strikes-and-armed-conflicts/
- AirHelp, "Airlines' favorite loophole: extraordinary circumstances" — https://www.airhelp.com/en-int/blog/extraordinary-circumstances/

### Tax

- MoneySavingExpert forum, "Flight delay compensation taxable?" — https://forums.moneysavingexpert.com/discussion/3695807/flight-delay-compensation-taxable
- Pinsent Masons, "Will your UK damages be taxable?" — https://www.pinsentmasons.com/out-law/guides/will-your-damages-be-taxable
- AccountingWEB, "Flight compensation on business flight?" — https://www.accountingweb.co.uk/any-answers/flight-compensation-on-business-flight
