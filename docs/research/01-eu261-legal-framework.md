# EU261/2004 Legal Framework: Flight Delay Compensation

**Research memo 01 — Legal framework for a delay-compensation arbitrage analysis**
_Prepared: 2026-07-04. Status: research-grade summary, not legal advice._

---

## 1. The Regulation and Compensation Tiers

**Regulation (EC) No 261/2004** of the European Parliament and of the Council (11 February 2004) establishes common rules on compensation and assistance to passengers in the event of **denied boarding, cancellation, or long delay of flights**. It repealed Regulation (EEC) No 295/91 and has applied since 17 February 2005.

### 1.1 Article 7 compensation amounts (fixed, per passenger)

| Band   | Great-circle distance                               | Compensation |
| ------ | --------------------------------------------------- | ------------ |
| Short  | ≤ 1,500 km                                          | **€250**     |
| Medium | 1,500–3,500 km, and all intra-EU flights > 1,500 km | **€400**     |
| Long   | > 3,500 km (extra-EU)                               | **€600**     |

- Distance is measured by the **great-circle method** to the **final destination** (Art. 7(4)). For connecting itineraries, the CJEU held in _Bossen v Brussels Airlines_ (C-559/16, 7 September 2017) that the relevant distance is the **direct great-circle distance between origin and final destination**, not the sum of the legs.
- Compensation is **per passenger**, independent of ticket price. A €15 promotional Wizz Air fare and a €400 flexible fare carry the same €250 entitlement. This asymmetry (compensation ≫ fare on budget carriers) is the economic core of the arbitrage thesis.
- **50% reduction** (Art. 7(2)): the carrier may halve compensation if it offers re-routing that arrives within 2 / 3 / 4 hours (by band) of the original scheduled arrival. Practical consequence for the EV engine: long-haul (> 3,500 km) arrivals delayed 3–4 h are routinely paid at the halved rate (€300 / £260) where the flight itself is treated as the re-routing; model $K$ as delay-dependent for the long band.
- Payment must be **cash, electronic bank transfer, bank orders or bank cheques**; vouchers/travel credit only **with the passenger's signed agreement** (Art. 7(3)). This defeats the common Wizz Air "Wizz credit" substitution tactic.

### 1.2 The 3-hour delay rule — _Sturgeon_ (C-402/07 and C-432/07)

The text of Reg. 261/2004 grants fixed compensation only for cancellation and denied boarding; for delay it grants care (Art. 9) and, from 5 hours, a refund (Art. 6). In **_Sturgeon v Condor; Böck and Lepuschitz v Air France_** (Joined Cases C-402/07 and C-432/07, judgment of 19 November 2009), the Court of Justice held, on the principle of equal treatment, that passengers whose flights are **delayed by three hours or more at final destination** must be treated like cancelled-flight passengers and are entitled to Article 7 compensation, unless the delay is caused by extraordinary circumstances. This was confirmed by the Grand Chamber in _Nelson v Lufthansa_ (Joined Cases C-581/10 and C-629/10, 23 October 2012).

**Key consequence:** what matters is **delay at arrival, not at departure**. A flight that departs 3.5 hours late but makes up time in the air and arrives 2 h 55 min late pays **nothing**. Conversely, a flight that departs on time but arrives 3 h+ late (diversion, holding) pays in full.

### 1.3 "Arrival time" = doors open — _Germanwings v Henning_ (C-452/13)

In **_Germanwings GmbH v Ronny Henning_** (C-452/13, 4 September 2014), the CJEU defined "actual arrival time" as **the moment at which at least one aircraft door is opened** and passengers are permitted to leave — not touchdown, not on-block time. In _Henning_, touchdown was at +2 h 58 min but doors opened at ~+3 h 03 min, tipping the flight over the threshold. Practical implications for modeling:

- Add **~5–10 minutes** to published "gate arrival" (on-block) times when estimating door-open time; ADS-B/OAG "arrival" fields typically record touchdown or on-block, so flights recorded at ~2 h 50 min+ gate delay may in fact be compensable.
- Marginal cases (delays of 2 h 55 – 3 h 05) are litigated on exactly this definition; carriers' own ACARS door-sensor data is the usual evidence.

### 1.4 Delay ≥ 5 hours

Independently of compensation, a delay of **5 hours or more** triggers the Art. 8(1)(a) right to a **full refund** of the ticket (and a return flight to the first point of departure where relevant) if the passenger chooses not to travel. Note: taking the refund and abandoning the journey means the passenger did not suffer the arrival delay — see §3 on the boarding requirement; refund and Art. 7 compensation for a delay actually suffered are, however, cumulable if the passenger travels.

### 1.5 Right to care (Art. 9)

From 2 hours' delay (band-dependent): meals and refreshments proportionate to waiting time, two communications, and hotel + transfer if an overnight stay becomes necessary. No extraordinary-circumstances defence applies to care obligations (_McDonagh v Ryanair_, C-12/11 — ash cloud; care owed even in "super-extraordinary" circumstances).

---

## 2. UK261 — The Post-Brexit Regime

EU261 was retained in UK domestic law (with sterling amounts) by the **Air Passenger Rights and Air Travel Organisers' Licensing (Amendment) (EU Exit) Regulations 2019 (SI 2019/278)**, amending retained Regulation (EC) 261/2004 — commonly "UK261."

| Band                                                    | Distance | UK261    |
| ------------------------------------------------------- | -------- | -------- |
| ≤ 1,500 km                                              | short    | **£220** |
| 1,500–3,500 km (and internal UK/EU > 1,500 km analogue) | medium   | **£350** |
| > 3,500 km                                              | long     | **£520** |

- **Scope:** all flights **departing a UK airport** (any carrier); flights **arriving into the UK** on a **UK or EU carrier**; substance mirrors EU261 including the _Sturgeon_ 3-hour rule and pre-Brexit CJEU case law (retained EU case law, persuasive/binding per the EU Withdrawal Act 2018 as amended).
- Post-2020 CJEU judgments (e.g., the 2024 _Laudamotion_ rulings, §3.3) are **not binding** on UK courts but are commonly cited as persuasive.
- A UK-departing flight on an EU carrier is covered by **both** regimes' logic but compensation can only be claimed **once** (no stacking of UK261 + EU261 for the same flight).
- Enforcement: **UK Civil Aviation Authority (CAA)**; limitation period in England & Wales: **6 years** (Limitation Act 1980, s.9) — 5 years in Scotland.

---

## 3. Eligibility: Check-in, Boarding, and the "Must You Actually Fly?" Question

This is the decisive issue for any "buy ticket, don't travel, collect €250" variant of the strategy. **Answer: you must present yourself for check-in in good time and, for delay compensation, you must actually take the flight (or a carrier-provided re-routing) and suffer the 3 h+ loss of time at your final destination. A ticket alone is not a lottery ticket.**

### 3.1 The regulation text — Article 3(2)

Reg. 261/2004 applies on condition that passengers:

> "(a) have a confirmed reservation on the flight concerned and, **except in the case of cancellation referred to in Article 5, present themselves for check-in**, — as stipulated and at the time indicated in advance … or, if no time is indicated, **not later than 45 minutes before the published departure time**; or (b) have been transferred by an air carrier or tour operator from the flight for which they held a reservation to another flight, irrespective of the reason."

- **Delay and denied-boarding claims** therefore require timely presentation for check-in.
- **Cancellation claims do not** — logically, one cannot check in for a cancelled flight (confirmed in _Airhelp v Laudamotion_, C-263/20, and Commission Interpretative Guidelines). For cancellations a confirmed reservation suffices; compensation depends on the Art. 5(1)(c) notice windows (cancellation < 14 days before departure, subject to the re-routing timing carve-outs).

### 3.2 Proof of check-in — _LC and MD v easyJet_ (C-756/18, order of 24 October 2019)

French courts had been dismissing delay claims where passengers could not produce boarding passes. The CJEU held (reasoned order) that Reg. 261/2004, in particular Art. 3(2)(a), must be interpreted as meaning that passengers of a flight delayed 3 h+ **cannot be refused compensation solely because they did not prove their presence at check-in** (e.g., by boarding card):

> "passengers … who hold a confirmed reservation on a flight **and have taken that flight**, must be considered to have properly satisfied the requirement to present themselves for check-in."

The presumption is **rebuttable**: the airline may defeat it by showing the passenger **was not in fact transported** on the delayed flight (a matter for the national court, on the carrier's own manifest/boarding-scan data). Note carefully what this order does _not_ do: it does **not** dispense with the substantive requirement of having travelled — it presumes check-in _from the fact of having been transported_. Keep your boarding passes anyway; it shortens disputes.

### 3.3 Checked in but did not board — _Laudamotion v flightright_ (C-474/22) and _WY v Laudamotion and Ryanair_ (C-54/23), both 25 January 2024

Two judgments of 25 January 2024 close the "no-show arbitrage" door explicitly:

- **_C-474/22 (Laudamotion GmbH v flightright GmbH):_** passenger held a confirmed reservation Düsseldorf → Palma; the flight was announced as delayed, he **chose not to take it** (fearing he would miss a business meeting); the flight ultimately arrived +3 h 32 min. The CJEU held he is **not entitled to Article 7 compensation**: the fixed compensation redresses the **loss of time of three hours or more actually suffered**; a passenger who did not go to the airport / did not take the flight did not suffer that loss. Compliance with the Art. 3(2)(a) check-in presentation requirement is a **precondition** of the delay claim.
- **_C-54/23 (WY v Laudamotion GmbH and Ryanair DAC):_** passenger, informed of a ~6 h delay, **self-rebooked** onto an alternative flight and reached the final destination **less than 3 hours** after the original scheduled arrival. No compensation: no relevant loss of time was suffered. (Any recoverable damage from self-help re-routing costs is a matter for national law / Montreal Convention, not Art. 7.)

**Synthesis of the case law:**

| Scenario                                                                                                         | Art. 7 compensation?                                 |
| ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Confirmed reservation, checked in, **flew**, arrived ≥ 3 h late (doors-open)                                     | **Yes** (absent extraordinary circumstances)         |
| Confirmed reservation, flight **cancelled** (< 14 days' notice, re-routing outside Art. 5 windows)               | **Yes** — no check-in required                       |
| Checked in online, **did not board**, flight arrived ≥ 3 h late                                                  | **No** (C-474/22 — loss of time not suffered)        |
| Did not present for check-in at all, flight delayed                                                              | **No** (Art. 3(2)(a); C-474/22)                      |
| Self-rebooked, arrived < 3 h late                                                                                | **No** (C-54/23)                                     |
| Took **carrier-provided** re-routing after cancellation/denied boarding, arrived ≥ 3 h late vs original schedule | Yes (delay measured against original itinerary)      |
| Denied boarding against will (overbooking), presented on time                                                    | Yes (Art. 4; no extraordinary-circumstances defence) |

**Strategic implication:** the arbitrage cannot be run as a pure financial position ("buy and forget"). The claimant must **physically make the journey** — check in, be at the gate, board, and land ≥ 3 h late. The realistic version of the strategy is therefore "fly routes you would fly anyway (or are willing to fly), weighted toward high-delay-probability flights," with the passenger's time on board and delay-hours as a real cost input to the expected-value model.

### 3.4 Ancillary eligibility points

- **Free/industry tickets excluded** (Art. 3(3)): passengers travelling free or at a reduced fare **not available directly or indirectly to the public** are excluded. Public promo fares (Wizz €9.99 sales, Ryanair €14.99 seats) **are** covered — a reduced fare available to the public is expressly protected.
- **Confirmed reservation** can be evidenced by the booking confirmation itself; _Azurair and Others_ (Joined Cases C-146/20, C-188/20, C-196/20, C-270/20, 21 December 2021) held that a tour-operator confirmation can suffice even if the airline disputed it.
- Compensation rights are **assignable** to claim agencies in most jurisdictions (contractual anti-assignment clauses have been struck down repeatedly, e.g., UK County Court appeals against easyJet; German BGH practice re flightright's assignment model).

---

## 4. Extraordinary Circumstances (Art. 5(3)) — the Carrier's Only Real Defence

The carrier escapes compensation (never care) if it proves the disruption was caused by **"extraordinary circumstances which could not have been avoided even if all reasonable measures had been taken."** Recital 14 lists examples (political instability, weather, security risks, unexpected flight-safety shortcomings, strikes affecting operations). The CJEU construes the defence **narrowly**; the burden of proof is on the carrier. The two-limb test from the case law: the event must (i) **not be inherent in the normal exercise** of the carrier's activity and (ii) be **outside its actual control**.

### 4.1 Not extraordinary (compensation payable)

| Event                                                                   | Authority                                                                                                                          |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Technical faults revealed in maintenance or from failure to maintain    | **_Wallentin-Hermann v Alitalia_** (C-549/07, 22 December 2008)                                                                    |
| Premature failure of parts, even unexpected                             | **_van der Lans v KLM_** (C-257/14, 17 September 2015)                                                                             |
| "Wildcat" staff sickness strike triggered by restructuring announcement | **_Krüsemann and Others v TUIfly_** (C-195/17 etc., 17 April 2018)                                                                 |
| Lawful union strike by the carrier's **own staff** over pay             | **_Airhelp v SAS_** (C-28/20, Grand Chamber, 23 March 2021)                                                                        |
| Unexpected death/illness of a crew member shortly before departure      | **_TAP v flightright_** (C-156/22 to C-158/22, 11 May 2023)                                                                        |
| Ordinary winter conditions / routine de-icing                           | German BGH, **X ZR 146/23** (de-icing inherent in normal winter operations; even airport fluid shortage rejected as extraordinary) |
| Knock-on delay from the carrier's own rotational scheduling (generally) | national case law applying the reasonable-measures limb                                                                            |

### 4.2 Extraordinary (no compensation, care still owed)

| Event                                                                                                                          | Authority / basis                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Genuinely exceptional weather incompatible with safe operation of the flight concerned                                         | Recital 14; national practice — **but see §4.3: ordinary/foreseeable weather and de-icing increasingly held compensable** |
| Air traffic management/ATC decisions and ATC strikes                                                                           | Recital 15; _TAP v flightright_ line                                                                                      |
| Bird strike                                                                                                                    | **_Pešková v Travel Service_** (C-315/15, 4 May 2017)                                                                     |
| Runway/airport closure, foreign-object damage                                                                                  | _Moens v Ryanair_ (C-159/18) (fuel spill closing runway)                                                                  |
| Hidden manufacturing defects flagged by manufacturer/authority; sabotage/terrorism                                             | _Wallentin-Hermann_, obiter                                                                                               |
| Unruly passenger causing diversion                                                                                             | _LE v TAP_ (C-74/19, 11 June 2020) (with conditions)                                                                      |
| **Airport staff / third-party strikes** (e.g., airport security, ground handlers not employed by carrier), general ATC strikes | Recital 14/15; Commission Interpretative Guidelines                                                                       |

Even where circumstances are extraordinary, the carrier must show it took **all reasonable measures** (spare aircraft, crew reserves, timely re-routing — _Pešková_; _Transportes Aéreos Portugueses_, C-74/19). Knock-on effects of an extraordinary event on a **previous rotation** of the same aircraft can be invoked only where there is a **direct causal link** to the claimed flight's delay (_TAP_, C-74/19; confirmed with an individualised-causal-analysis requirement by the General Court, 21 January 2026) — remote or attenuated knock-ons fail. And where the carrier's **own operational choices** intervene (e.g., voluntarily holding an aircraft, resequencing rotations), the CJEU held in March 2026 (European Air Charter, Cologne-Bonn reference) that the consequent delay to other flights is the carrier's own decision and **compensable** — an extraordinary circumstance does not travel through the schedule for free. This matters enormously for LCC point-to-point rotations.

### 4.3 Weather in detail — an affirmative defence, not a categorical exemption

The common shorthand "weather delays don't pay" is an overstatement. Recital 14 lists weather only as an example of what _may_ constitute extraordinary circumstances; the carrier must still prove **both limbs per flight** (not inherent + outside control, _and_ all reasonable measures taken), with the burden on the carrier and the defence construed narrowly. Weather-attributed delays **do pay** in at least six recurring scenarios:

1. **Ordinary, foreseeable weather.** Seasonal fog, routine winter conditions, common thunderstorms are increasingly held _inherent_ in normal operations. Sharpest statement: German BGH **X ZR 146/23** — cold and **de-icing are normal winter activity**, not extraordinary (even de-icing-fluid shortages rejected). English reasoning points the same way (_Huzar v Jet2_ [2014] EWCA Civ 791: extraordinary means out of the ordinary, "freak" for the route/season).
2. **Weather on a previous rotation without a direct causal link** to the claimed flight (C-74/19; General Court 21 Jan 2026 — individualised analysis per flight).
3. **The airline's own choices intervene** (March 2026 CJEU: the carrier's decision on how to absorb a disruption makes downstream delays compensable).
4. **Reasonable-measures failure** even in genuine weather: no spare aircraft/crew, no re-timing, no re-routing offered **including on other carriers** (C-74/19 §58–59). The LCC no-interline, no-spare operating model systematically struggles on this limb _after the weather clears_.
5. **Weather affected a different flight/airport, not "the flight concerned"** — blanket "weather in the network" rejections without flight-specific proof fail (and boilerplate weather rejections are what NEBs/ADR routinely overturn; cf. the CAA's Wizz Air enforcement).
6. **Weather-tagged ATFM slot delays without flight-specific causation** (post-Jan-2026 General Court: the specific ATM decision must be shown to have affected the specific flight). Note the same judgment confirms genuine ATC/ATM decisions beyond the airline's control **are** extraordinary.

Weather does **not** pay when genuinely severe conditions incompatible with safe operation of the specific flight are properly evidenced with a direct causal link and reasonable measures satisfied (closures, storms above operating limits, ash — _McDonagh_); then only duty of care (uncapped) is owed. Related conditional rulings: lightning strikes triggering mandatory inspections _can_ be extraordinary, but only with proven causation and reasonable measures (CJEU, Oct 2025).

**Modeling note:** for a delay-arbitrage EV model, the compensable-delay probability is _P(arrival delay ≥ 3 h) × P(cause not extraordinary | delay ≥ 3 h)_. Weather + ATC-attributed delays remain the dominant exclusions, but the eligibility model should **not zero out weather-coded delays**: a defensible decomposition is exceptional-weather (exempt) vs ordinary-weather/de-icing (substantially compensable, jurisdiction-dependent — strongest in Germany) vs weather-reactionary knock-on (compensable where the causal link is remote or reasonable measures failed). A realistic compensable share of weather-attributed 3h+ delays is plausibly **20–40%, not ~0%**. Crew shortage, rotational knock-on (own-fault), and technical faults — a large share of LCC long delays — remain compensable. **Caveat: no published statistic pins down the overall share of 3h+ delays that are compensable; treat the eligibility haircut as an unvalidated assumption and a headline sensitivity axis.**

---

## 5. Claim Process, Limitation Periods, and Enforcement Friction

### 5.1 Time limits — set by national law

Reg. 261/2004 contains no limitation period. **_Cuadrench Moré v KLM_** (C-139/11, 22 November 2012): time limits for actions are determined by **each Member State's national rules**, subject to equivalence and effectiveness. Selected periods:

| Jurisdiction                                                                    | Limitation period                                                          |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **UK (England & Wales)**                                                        | **6 years** (5 in Scotland)                                                |
| **Ireland**                                                                     | 6 years                                                                    |
| **Germany**                                                                     | **3 years** (BGB §195, from end of the year the claim arose)               |
| Austria, Denmark, Finland, Norway, Portugal, Romania, Czech Rep., Baltic states | ~3 years                                                                   |
| **France, Spain**                                                               | 5 years                                                                    |
| Croatia, Netherlands, Slovakia, Slovenia                                        | ~2 years                                                                   |
| **Italy**                                                                       | 2 years international / 26 months–1 year domestic quirks                   |
| Belgium, Poland                                                                 | 1 year (Poland: 1 year with case-law wrinkles); Sweden 10 years (contract) |

Jurisdiction/venue: under _Rehder v Air Baltic_ (C-204/08, 9 July 2009), the passenger may sue at the **place of departure or the place of arrival** (Brussels I recast Art. 7(1)), at the passenger's election — practically important for suing Hungarian-registered Wizz Air in the passenger's local small-claims court.

### 5.2 How airlines resist — LCC payout behaviour

- **First-response denial:** boilerplate "extraordinary circumstances" rejections (weather/ATC cited without evidence) are common; a substantial share of initially rejected claims succeed on escalation.
- **Wizz Air:** documented worst-in-class. The UK CAA's enforcement action (announced 17 January 2024) forced Wizz Air to **re-open ~25,000 rejected claims and pay out ~£1.24 million** it had wrongfully denied (mostly re-routing/care expenses, plus compensation). Known tactics: offering **"Wizz credit"** instead of cash (non-compliant with Art. 7(3) absent signed consent), slow-walking, ignoring ADR deadlines. Wizz Air is subject to Hungarian NEB oversight for EU matters and CAA for UK.
- **Ryanair:** high initial-rejection rate, aggressive litigation posture, historically withdrew from the UK's AviationADR scheme (2018–), attempts to bar claim-agency assignments via its T&Cs and to require direct claims first; repeated adverse UK county-court and German rulings on those clauses. Pays reliably once litigation is issued in clear-cut cases (usually settles before hearing).
- **easyJet:** middling; participates in ADR (CEDR in the UK); lost the notable appeal upholding **assignment** of EU261 claims to agencies.

### 5.3 Escalation ladder (typical cost/latency)

1. **Direct claim** to the airline (webform; keep boarding passes, delay evidence, e.g., FlightAware/Flightradar24 logs). Cost: €0. Latency: 2–8 weeks. LCC first-pass payout rate is materially < 100% even on valid claims.
2. **National Enforcement Body (NEB)** complaint (Art. 16): e.g., UK CAA (via PACT), German LBA, Hungarian authority for Wizz Air EU claims. NEBs sanction carriers but in most states do **not** award individual compensation (CJEU _Ruijssenaars_, C-145/15: NEB action is optional enforcement, not an individual remedy) — Hungary is a notable exception where the consumer-protection authority can order payment.
3. **ADR scheme** where the airline subscribes (UK: CEDR / AviationADR; Germany: söp). Binding-ish on airline, free or ~£25 for the passenger.
4. **Claim agencies** (no-win-no-fee): **AirHelp** — 35% service fee, **+15% legal-action fee** (up to 50% all-in, VAT incl.); **Flightright** — 20–30% + ~14% if lawyers engaged (~50% all-in worst case); Skycop, ClaimCompass similar. They absorb litigation risk and airline stonewalling; economically sensible only if you value your time highly or the airline stonewalls.
5. **Small claims court**: European Small Claims Procedure (claims ≤ €5,000, cross-border) or national small-claims track (UK MCOL up to £10,000; German Mahnverfahren). Fees modest and recoverable on win; LCCs settle most well-documented claims pre-hearing.

**EV modeling note:** expected recovery = statutory amount × P(valid claim) × P(collection). For self-managed claims against Wizz/Ryanair, realistic collection on _valid_ claims approaches ~90%+ but with 1–12 month latency and nonzero effort cost; via agencies, multiply by 0.50–0.75.

---

## 6. Territorial and Carrier Scope (Art. 3(1))

| Flight                                                                                                                                                | Covered by EU261?     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| Departing an airport in the EU/EEA (incl. outermost regions; also CH by agreement for EU carriers) — **any carrier**                                  | **Yes**               |
| Arriving into the EU from a third country — **EU ("Community") carrier only**, and not if benefits/compensation already received in the third country | **Yes** (conditional) |
| Arriving into the EU from a third country on a **non-EU carrier**                                                                                     | **No**                |
| Wholly outside the EU                                                                                                                                 | No                    |

UK261 mirrors this: departing UK (any carrier); arriving UK on UK/EU carrier.

**Carrier status of the target LCCs** (the _operating_ carrier's licence controls — Art. 2(b); _Wirth_, C-532/17):

- **Wizz Air Hungary** (W6): EU carrier → covered on all EU departures **and** all arrivals into the EU/UK (e.g., Tel Aviv→Budapest, Tbilisi→Rome). **Wizz Air UK** (W9): UK carrier → UK261 both directions UK-touching; EU261 when departing EU. **Wizz Air Malta** (W4): EU carrier. **Wizz Air Abu Dhabi** (5W): **UAE carrier** — covered only on flights _departing_ the EU, **not** on AUH→EU sectors.
- **Ryanair** (FR, Irish AOC; also Malta Air/Buzz/Lauda Europe subsidiaries, all EU AOCs): effectively covered on its entire network (almost wholly intra-EU/UK).
- **easyJet**: easyJet UK (U2, UK AOC), easyJet Europe (EJU, Austrian AOC), easyJet Switzerland (DS): all flights on its European network are covered by EU261 and/or UK261.

Practical upshot: on Wizz/Ryanair/easyJet intra-European networks, **essentially every flight is in scope**, and most sectors are ≤ 1,500 km (€250/£220) with a meaningful 1,500–3,500 km tail (€400/£350) on East–West and Canaries/Middle East routes.

---

## 7. Anti-Abuse: Is "Compensation Hunting" Penalised?

### 7.1 No intent requirement in the regulation or case law

Reg. 261/2004 contains **no provision conditioning compensation on the passenger's motive** for booking. Compensation is standardized redress for objectively suffered loss of time (_Sturgeon_; _Nelson_). Research found **no CJEU or reported national appellate decision denying compensation because the passenger deliberately selected a delay-prone flight**. Eligibility turns on objective facts: confirmed reservation, publicly available fare, timely presentation, transportation, arrival delay, cause. A passenger who books a statistically delay-prone 21:55 Luton–Bucharest rotation _hoping_ it is late, flies it, and lands 3 h+ late is legally indistinguishable from any other passenger on board.

Caveats and residual risks:

- **General EU abuse-of-rights doctrine** (e.g., _Kofoed_, C-321/05; _Cussens_, C-251/16) exists in principle: rights conferred by EU law may not be relied upon for abusive ends (wholly artificial arrangements defeating the provision's purpose). It has never been applied to EU261 passenger claims. The nearest modern authority is **_Brillen Rottler_ (C-526/24, 19 March 2026)** — a GDPR access-request/compensation case in which the CJEU held that deliberately **manufacturing the conditions for a damages claim** can break the causal chain to compensable damage and render even a first request abusive (objective element + subjective intent, burden on the defendant, narrowly construed). The analogy to EU261 is imperfect in the claimant's favor: a passenger who genuinely flies and genuinely loses 3+ hours suffers exactly the standardized harm the regulation compensates — the injury cannot be "manufactured" the way a data-access request can. The theoretical exposure is highest for contrived setups (e.g., booking with no intention or ability to complete travel — which C-474/22 already defeats on its own terms).
- **The 2024 Laudamotion pair is itself the anti-abuse backstop**: by anchoring compensation to time-loss actually suffered, the CJEU eliminated all no-fly variants (§3.3).
- **Carrier-side retaliation** is the practical risk: LCC T&Cs permit refusing carriage/closing accounts of passengers deemed abusive (Ryanair has litigated against screen-scrapers and "chargeback abusers"; airlines have blacklisted serial claimants' accounts). This is a commercial/contractual risk, not a bar to accrued statutory claims, but repeated claiming under one account/name is observable to the airline.
- **Denied boarding does not help the airline**: bumping a suspected compensation-hunter who presented on time simply creates an Art. 4 denied-boarding claim with **no** extraordinary-circumstances defence.

### 7.2 Connecting-flight amplification — _Folkerts_ (C-11/11)

**_Air France v Folkerts_** (C-11/11, 26 February 2013): compensation depends on **delay at the final destination of a single booking**, regardless of whether the delay arose at departure, en route, or via a missed connection, and regardless of whether any individual leg was delayed ≥ 3 h. Mrs Folkerts' Bremen→Paris→São Paulo→Asunción itinerary left Bremen 2.5 h late, cascaded through missed connections, and arrived 11 h late: full €600.

Tactical corollaries for the strategy:

- **Short first leg + tight connection on one ticket** turns a modest inbound delay into a long-band payout measured at the final destination (distance = direct origin→destination great circle, _Bossen_).
- The itinerary must be a **single reservation**; self-connecting separate LCC tickets do _not_ aggregate (each flight assessed alone; missed self-connection is the passenger's risk). Note Wizz and Ryanair sell almost exclusively point-to-point single-leg tickets — connection amplification mostly applies to network carriers or LCC "connected" products (e.g., easyJet Worldwide via Gatwick has contractual, not EU261-aggregated, protection).

---

## 8. Regulatory Risk: The EU261 Reform (agreed June 2026 — 3h threshold kept)

The Commission's 2013 revision proposal (COM(2013) 130) was revived in 2025 and has now been substantially resolved:

- **Council general approach (5 June 2025):** raise delay-compensation thresholds to **4 hours** (journeys ≤ 3,500 km / intra-EU, €300) and **6 hours** (> 3,500 km, €500). Analyses suggested 60–70% of currently compensable passengers would have lost entitlement.
- **European Parliament position (2025–26):** retain the **3-hour** threshold.
- **Outcome — provisional political agreement, conciliation, ~12–15 June 2026:** the deal **keeps the 3-hour threshold and the €250/€400/€600 amounts**. The Council's 4h/6h proposal did not survive. New elements: a **30-day deadline for airlines to pay or give reasons** once a claim is filed (a material _reduction_ in collection friction), a duty to inform passengers of their rights within 96 hours, a guaranteed free small cabin bag, and adjacent seating for children. Codified extraordinary-circumstances lists are expected in the final text.
- **Residual risk:** the text awaits plenary approval (expected July 2026) and would apply from ~2027; the final wording of the extraordinary-circumstances annex could move the eligibility haircut in either direction, and the UK would not automatically follow. The 4h/6h scenario should be retained in the backtest only as a historical stress case, not as the base regulatory forecast.

---

## 9. Key Takeaways for the Arbitrage Model

1. Payout is fare-independent: €250/£220 on < 1,500 km sectors dominates the LCC opportunity set; typical Wizz/Ryanair fares of €15–60 imply gross multiples of 4–16× **conditional on** a compensable 3 h+ arrival delay.
2. The binding constraint is **you must actually fly** (C-474/22): cost basis = fare + travel time + delay time + positioning, not just fare.
3. Compensable-delay probability per flight is low (3 h+ arrival delays alone are ~0.7–1% of flights; ~1.5% including cancellations; net of extraordinary circumstances, lower), so EV per booking is usually negative unless flights are selected on strong delay predictors (evening rotations, congested airports, known-disrupted operations) **and** the traveler would fly anyway.
4. Collection friction (denials, latency, agency cuts of 25–50%) is a first-order haircut on any backtested edge. The 2026 reform agreement (§8) removed the 4 h/6 h threshold risk and will, if enacted, _reduce_ friction via the 30-day payment deadline.
5. **Montreal Convention interplay (for completeness):** MC99 Art. 19/22 delay damages (up to ~5,346 SDR) are additional, fault-based, proof-of-actual-loss recovery, cumulable with EU261 subject to the Art. 12 offset (national practice deducts EU261 from proven damages). Irrelevant to the fixed-payout arbitrage.

---

## Sources

**Primary law and official guidance**

- Regulation (EC) No 261/2004, consolidated text — https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32004R0261
- Retained UK version (legislation.gov.uk) — https://www.legislation.gov.uk/eur/2004/261/contents
- Commission Interpretative Guidelines on Reg. 261/2004 (2024 update, OJ C/2024/5687) — https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:C_202405687
- European Commission / DG MOVE, "Air passenger rights — European case law" summary (March 2022) — https://transport.ec.europa.eu/system/files/2022-03/2022-summary-of-the-most-relevant-cjeu-judgements.pdf
- Your Europe — Air passenger rights — https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm
- UK CAA — Delays — https://www.caa.co.uk/air-passengers/travel-problems-and-rights/flight-delays-and-cancellations/delays/ ; rejected claims — https://www.caa.co.uk/passengers-and-public/resolving-travel-problems/delays-and-cancellations/making-a-claim/what-to-do-if-your-claim-is-rejected/

**Case law (CJEU unless noted)**

- _Sturgeon and Others_ (C-402/07 & C-432/07, 19 Nov 2009) — https://www.flight-delayed.com/en/sturgeon-ruling ; https://en.wikipedia.org/wiki/Air_Passengers_Rights_Regulation
- _Germanwings v Henning_ (C-452/13, 4 Sep 2014) — https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A62013CJ0452_SUM ; https://www.bottonline.co.uk/flight-delay-compensation/claim-guides/definition-of-arrival-time
- _LC and MD v easyJet_ (C-756/18, order 24 Oct 2019) — https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62018CO0756
- _Laudamotion v flightright_ (C-474/22, 25 Jan 2024) — https://eur-lex.europa.eu/legal-content/AUTO/?uri=CELEX%3A62022CJ0474 ; commentary: https://aire.aero/ecj-case-474-22-laudamotion-and-c-54-23-laudamotion-and-ryanair/ ; https://www.shb-law.at/en/post/current-ecj-judgement-on-air-passenger-rights-no-lump-sum-payment-in-case-of-flight-delay-if-the-pa
- _WY v Laudamotion and Ryanair_ (C-54/23, 25 Jan 2024) — https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A62023CJ0054
- _Wallentin-Hermann v Alitalia_ (C-549/07, 22 Dec 2008) — https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A62007CJ0549 ; https://iftta.org/news/ecj-case-c-549-07-wallentin-hermann-v-alitalia/
- _Krüsemann v TUIfly_ (C-195/17 etc., 17 Apr 2018) — https://www.twobirds.com/en/insights/2018/global/ecj-delivers-two-judgments-in-relation-to-extraordinary-circumstances-reg-261
- _Airhelp v SAS_ (C-28/20, 23 Mar 2021) — https://www.ecc.fi/en/themes/travelling/air-travel/rulings-of-the-court-of-justice-of-the-european-union/
- _Air France v Folkerts_ (C-11/11, 26 Feb 2013) — http://recent-ecl.blogspot.com/2013/02/compensation-for-delayed-connecting.html ; https://iftta.org/news/european-court-of-justice-compensation-for-flight-delay-not-conditional-upon-delay-at-departure/
- _Cuadrench Moré v KLM_ (C-139/11, 22 Nov 2012) — https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62011CJ0139 ; https://iftta.org/news/ecj-clarifies-time-limit-for-court-actions-under-eu-air-passenger-rights-regulation/
- Gatwick connections / non-EU carrier liability (English CA) — https://www.hfw.com/insights/eu261-english-court-of-appeal-finds-non-eu-airlines-liable-for-missed-connections-october-2017/
- easyJet assignment appeal — https://1ec.co.uk/easyjet-loses-appeal-as-court-upholds-assignment-of-eu261-compensation-claims/

**UK261 and practice**

- Flightright UK — UK261 amounts and Brexit — https://www.flightright.co.uk/your-rights/eu-regulation ; https://www.flightright.co.uk/your-rights/air-passenger-rights-brexit
- AirHelp UK261 guide — https://www.airhelp.co.uk/uk-261/
- Skycop UK261 overview — https://www.skycop.com/us/uk-261-flight-delay-cancellation-compensation/

**Enforcement, agencies, airline behaviour**

- Compens.AI — CAA/Wizz Air £1.24m enforcement — https://compens.ai/en/articles/flight-compensation-uk-2025-uk261-wizz-air-british-airways-delays
- Wizz Air EC261 help page — https://www.wizzair.com/en-gb/help-centre/my-wizz-account/claims-and-compensation/ec261-regulation
- AirHelp price list (35% + 15%) — https://www.airhelp.com/en/price-list/ ; fee sheet PDF — https://img.airhelp.com/Legal/fees/F1_23/F1.23_EN___Our_Fees___AirHelp.pdf
- Flightright costs (20–30% + 14%) — https://www.flightright.com/costs
- ClaimFlights — limitation periods by country — https://claimflights.com/time-limit-for-eu-claims/ ; SkyRefund — https://skyrefund.com/en-us/blog/time-limit-flight-delay-compensation

**Reform (regulatory risk)**

- Council press release, general approach (5 Jun 2025) — https://www.consilium.europa.eu/en/press/press-releases/2025/06/05/council-sets-position-on-clearer-and-improved-rules-for-air-passengers/
- EP Legislative Train — revision of 261/2004 — https://www.europarl.europa.eu/legislative-train/spotlight-JD22/file-common-rules-on-compensation-to-passengers
- EP press release (Jan 2026, Parliament position) — https://www.europarl.europa.eu/news/en/press-room/20260116IPR32442/european-parliament-stands-behind-air-passenger-rights
- Flight-Delayed — reform agreement (12 Jun 2026, 3h threshold kept) — https://www.flight-delayed.com/en/news/2026/06/12/eu-air-passenger-rights-reform-agreement
- AeroMorning — reform compromise analysis — https://aeromorning.com/en/eu261-reform-a-compromise-with-no-winners-in-europe/
- AirRefund — reform summary (16 Jun 2026) — https://www.airrefund.com/en/blog/2026/06/16/eu261-reform-passenger-rights-2026

**Weather / extraordinary-circumstances nuance (§4.3)**

- Lexology — German BGH X ZR 146/23 de-icing decision — https://www.lexology.com/library/detail.aspx?g=ecf50d02-df73-496b-8519-933d2f98d34a
- EUobserver — CJEU March 2026, airline's own choice breaks the extraordinary-circumstances chain — https://euobserver.com/205626/when-a-european-airline-chooses-to-delay-they-still-must-pay-ecj-rules/
- Augusta Abogados — General Court judgment 21 Jan 2026 on extraordinary circumstances — https://augustaabogados.com/en/the-three-key-takeaways-from-the-general-court-judgment-of-21-january-2026-a-turning-point-in-the-interpretation-of-extraordinary-circumstances-under-regulation-261-2004/
- AIRE — CJEU Oct 2025 lightning-strike ruling — https://aire.aero/the-cjeu-clarifies-extraordinary-circumstances-in-case-of-lightning-struck-aircraft/
- CMS — C-526/24 _Brillen Rottler_ (GDPR abuse-of-rights) — https://cms.law/en/deu/legal-updates/cjeu-on-the-gdpr-abuse-of-rights-causation-and-compensation
- LexisNexis — C-156/22 crew death not extraordinary — https://www.lexisnexis.co.uk/legal/news/court-of-justice-confirms-unexpected-death-of-a-crew-member-prior-to-flight-departure-is-not
