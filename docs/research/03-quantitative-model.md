# 03 — Quantitative Model: EU261 Delay-Compensation Arbitrage

**Status:** Methodology draft — **every numeric parameter value in this document
($p_{\text{delay}}$, $p_e$, $p_\pi$, GPD parameters, worked-example EVs) is a placeholder
assumption, not a measurement.** The pipeline (PLAN.md Phases 1–6) replaces them with
estimates from data. The equations and estimator designs are the substance of this memo; the
numbers are illustrations of how the machinery behaves under assumed inputs.
**Scope:** Single-flight EV, delay-tail modeling, portfolio/Kelly sizing, backtest design,
worked examples, market-efficiency analogues.

---

## 0. Notation and setup

| Symbol             | Meaning                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| $c$                | Ticket cost (all-in fare, EUR)                                                                                |
| $K$                | EU261 Article 7 compensation: €250 (≤1,500 km), €400 (1,500–3,500 km or intra-EU >1,500 km), €600 (>3,500 km) |
| $D$                | Arrival delay at final destination (minutes), measured door-open time vs. schedule                            |
| $p_{\text{delay}}$ | $\Pr(D \ge 180)$                                                                                              |
| $p_{e}$            | $\Pr(\text{non-extraordinary cause} \mid D \ge 180)$ — "eligible given delayed"                               |
| $p_{\pi}$          | $\Pr(\text{claim actually paid} \mid \text{eligible})$ — enforcement/collection success                       |
| $p$                | $\Pr(\text{compensation collected}) = p_{\text{delay}} \cdot p_{e} \cdot p_{\pi}$                             |
| $\alpha$           | Claim-agency commission (typ. 25–35% + VAT) if not DIY                                                        |
| $\phi$             | Per-flight friction cost: search/booking time, claim filing time, payment friction, valued in EUR             |
| $f$                | Fraction of bankroll staked per flight (Kelly analysis)                                                       |

Two structural facts frame everything below:

1. **The bet is a low-probability, high-multiple binary payoff** — a lottery ticket with odds roughly $K/c \approx 10{:}1$ to $25{:}1$.
2. **The payoff trigger is not "delay ≥ 3h" but "delay ≥ 3h AND the cause is legally attributable to the carrier AND you get paid."** The wedge between $p_{\text{delay}}$ and $p$ is where the strategy dies, and — as §3.3 shows — the wedge is _adversely selected_: the delay causes that cluster (and would make a portfolio of tickets pay off together) are precisely the exempt ones.

Legal fine print that matters quantitatively:

- Delay compensation under _Sturgeon_ (C-402/07) / _Nelson_ (C-581/10) case law: ≥3h **arrival** delay is treated like cancellation for Article 7 purposes.
- Article 7(2)(c): compensation may be halved where the carrier offers re-routing arriving within 2/3/4 h (by band) of the original schedule — in practice, >3,500 km flights arriving 3–4 h late are routinely paid at €300 rather than €600. Model $K$ as delay-dependent for long-haul.
- You must hold a confirmed reservation and (for delay claims) actually travel. **The ticket cannot be treated as a pure financial option; exercising it costs a day of your life and puts you in the wrong city.** This is captured in $\phi$ and is the single most underrated cost.
- Cancellations announced <14 days before departure also trigger Article 7 (with re-routing-timing offsets). This adds a small second payoff leg; we note it in §1.4 and otherwise ignore it.

---

## 1. Single-flight expected value

### 1.1 EV and the payoff decomposition

Net payoff of one ticket (DIY claiming):

$$
X \;=\; K \cdot \mathbf{1}\{\text{paid}\} \;-\; c \;-\; \phi
$$

$$
\mathbb{E}[X] \;=\; pK - c - \phi, \qquad p = p_{\text{delay}} \cdot p_e \cdot p_\pi .
$$

With an agency taking commission $\alpha$, replace $K$ by $K_{\text{net}} = (1-\alpha)K$ (and reduce the claim-filing component of $\phi$).

The three-factor decomposition of $p$ is the modeling backbone:

- $p_{\text{delay}} = \Pr(D \ge 180)$: a statistical/ML estimation problem (§2). **Assumed
  prior (unmeasured):** fleet-wide European values on the order of ~1–2% (the claim-industry
  figure of ~1.5% of departures delayed ≥3h or cancelled, doc 02 §2, is the only published
  anchor), with worst carrier–route–time-slot cells plausibly several times that. The actual
  values per cell are Phase 2's first deliverable. Note that headline "disruption" statistics
  quoted by claim agencies (e.g., "1 in 3 Wizz Air / easyJet flights disrupted") count _all_
  delays >15 min plus cancellations and denied boarding — the ≥3h bucket is one to two orders
  of magnitude rarer.
- $p_e$: extraordinary-circumstances carve-out (Art. 5(3), _Wallentin-Hermann_ C-549/07). Claimable: most **technical faults** (inherent in normal operations), **crew shortages**, airline's **own staff strikes** (_Krüsemann_ C-195/17), **ordinary weather/de-icing** (German BGH X ZR 146/23) and remote weather knock-ons (C-74/19 direct-causal-link requirement — see doc 01 §4.3). Exempt: genuinely exceptional weather, ATC/ATFM restrictions, third-party strikes (ATC), airport closures, bird strikes (_Pešková_ C-315/15), medical diversions. Working assumption $p_e \approx 0.35\text{–}0.55$ for long delays — **unvalidated: no published statistic exists for the compensable share of 3h+ delays; treat as a headline sensitivity axis** — and it is lower exactly when $p_{\text{delay}}$ spikes (§3.3), though the weather nuance (20–40% of weather-tagged delays contestable) softens the floor.
- $p_\pi$: even for legally valid claims, carriers deny first-pass at high rates; national-enforcement-body queues and small-claims litigation raise the cost and delay of collection. Realistic $p_\pi \approx 0.75\text{–}0.9$ DIY-with-persistence, higher via agencies/lawyers (who charge $\alpha$ for exactly that).

Multiplying midpoints: $p \approx 0.02 \times 0.45 \times 0.85 \approx \mathbf{0.75\%}$ for a typical cheap flight; a well-selected worst-cell flight might reach $p \approx 0.035 \times 0.5 \times 0.85 \approx \mathbf{1.5\%}$.

### 1.2 Breakeven probability

Setting $\mathbb{E}[X] = 0$:

$$
p^\* \;=\; \frac{c + \phi}{(1-\alpha)K}.
$$

Naive frictionless version ($\phi = 0, \alpha = 0$): $p^\* = c/K$.

**Headline case:** $c = €25$, $K = €250$ → $p^\* = 10\%$. Under the assumed prior of a
collected-probability around 0.5–1.5% (unmeasured), the gap to breakeven would be **7–20×** —
whether real cells close it is the empirical question. Frictions raise the hurdle:

| Claiming mode                                | $\alpha$ | $\phi$ | $p^\*$ at $c=€25, K=€250$ |
| -------------------------------------------- | -------- | ------ | ------------------------- |
| Frictionless fantasy                         | 0        | €0     | **10.0%**                 |
| DIY (1h admin @ €15/h, ignoring travel time) | 0        | €15    | 16.0%                     |
| Agency (35%)                                 | 0.35     | €5     | 18.5%                     |
| DIY incl. valuing the travel day at even €30 | 0        | €45    | 28.0%                     |

Even before valuing your time in the airport, **the friction-adjusted breakeven is 16–19%,
not 10%** (given the friction assumptions above). What $p$ is actually achievable per cell is
unmeasured — the pipeline's job.

### 1.3 Breakeven frontier: required $p^\*$ as a function of $c$ and $K$

Frictionless $p^\* = c/K$ (add $\phi$ and divide by $(1-\alpha)$ for your operating mode):

| $c$ (€) | $K=250$ | $K=400$ | $K=600$ |
| ------: | ------: | ------: | ------: |
|       5 |    2.0% |   1.25% |   0.83% |
|      10 |    4.0% |    2.5% |    1.7% |
|      15 |    6.0% |   3.75% |    2.5% |
|      20 |    8.0% |    5.0% |    3.3% |
|      25 |   10.0% |   6.25% |    4.2% |
|      40 |   16.0% |   10.0% |    6.7% |
|      60 |   24.0% |   15.0% |   10.0% |
|     100 |   40.0% |   25.0% |   16.7% |

Read horizontally against achievable $p \in [0.5\%, 2\%]$: the frontier is crossed only in the extreme top-left corner — **fares ≤ €5–10 on €400–600 routes** — before frictions. As a chart: plot $c$ on the x-axis, $p$ on the y-axis; the three lines $p = (c+\phi)/((1-\alpha)K)$ partition the plane; shade the empirically reachable band $p \in [0.5\%, 3.5\%]$ as a horizontal strip near the floor. The strip intersects the feasible (EV>0) region only where promotional-fare density is thin and seat capacity is tiny (§4.5). Two structural ironies:

1. **$K$ doesn't scale with $c$.** The regulation makes $K$ a step function of distance while $c$ scales with distance and demand — so the best ratio $K/c$ lives on long, cheap routes (e.g., €19.99 fares on 1,600–2,500 km ultra-LCC routes where $K=€400$: $K/c = 20$). This is where all screening should concentrate.
2. **$c$ is endogenous to $p$.** Fares on chronically disrupted evening rotations are not discounted for delay risk (airlines price demand, not EU261 liability per seat — though EU261 liability does enter their network-level cost base). This is the only reason an "edge" is conceivable at all: the fare market does not clear on $p$.

### 1.4 Small correction terms

$$
\mathbb{E}[X] = \underbrace{p K_{\text{net}}}_{\text{delay comp}} + \underbrace{p_{\text{cxl}<14d}\, K'_{\text{net}}}_{\text{cancellation leg}} + \underbrace{\mathbb{E}[\text{care: meals, hotel}]}_{\text{Art. 9, in-kind}} + \underbrace{v_{\text{trip}}}_{\text{consumption value of flying}} - c - \phi .
$$

- The cancellation leg adds maybe 0.3–1% × $K$ adjusted for re-routing offsets — small positive. Backtest labels should also count carrier re-routing arriving ≥3h late as positives.
- **Missed connections on single bookings — the one channel that materially changes the EV geometry.** Per _Folkerts_ (C-11/11), compensation keys on delay at the **final destination** of a single reservation at the **full-itinerary distance band** (_Bossen_: direct origin→destination great circle). A €40 two-leg itinerary where a 40–60 min delay on leg 1 breaks the connection pays €400–600 at final arrival ≥3h late — and $\Pr(\text{connection break})$ (leg-1 delay ≥ connection slack, often 45–60 min) is **an order of magnitude above** $\Pr(D \ge 180)$ on a nonstop. Caveats that keep this from rescuing the strategy: the itinerary must be one reservation (self-connections don't aggregate); Wizz/Ryanair sell almost no connected products (network carriers and easyJet Worldwide-style products do, at higher fares); and the leg-1 delay must itself be non-exempt. Still, this deserves explicit screening and its own EV module before any "measure-zero" conclusion is finalized.
- Article 9 duty-of-care (meals ≥2h, hotel if overnight) is real and — unlike Art. 7 — **survives extraordinary circumstances** (_McDonagh_, uncapped). On a deliberate overnight-delay exposure it is €80–150 of in-kind value and is the _only_ payoff on systemic-tail days, partially offsetting the §3.3 adverse selection. In-kind, receipts required, and you must want to be there — price it, but don't bank it.
- **Schedule-change kill switch (negative):** LCCs re-time or cancel >14 days out routinely on thin routes (~3–10% of months-ahead bookings); your selected rotation position evaporates into a refund or a re-timed flight and EV resets to ~$-\phi$. A direct multiplicative haircut on $p$ missing from naive EV formulas.
- **Multi-passenger amortization (positive, mostly for the overlay case):** one booking with $n$ passengers pays $n \times K$ while search/claim friction $\phi$ is largely per-booking — friction per euro of $K$ drops ~$n$×.
- Recoverable court fees and statutory interest on small-claims wins slightly reduce the effective $\alpha/p_\pi$ haircut for the persistent DIY claimant (small positive).
- $v_{\text{trip}}$ is the honest rescue: **if you wanted to take the flight anyway, $c$ is sunk consumption and the claim is a free overlay with unambiguous EV > 0.** The _arbitrage_ framing (flying purely to collect) is what the rest of this document evaluates — and it requires $pK_{\text{net}} > c + \phi$ with $v_{\text{trip}} = 0$ (or negative: you must also get home).

---

## 2. Modeling the delay distribution

### 2.1 Mixture structure

Arrival delay is not remotely Gaussian. Empirically it is a **mixed distribution**: substantial mass at/below zero (early or on-time arrivals — schedule padding makes $\Pr(D \le 0) \approx 0.4\text{–}0.6$), a bulk of small positive delays, and a **heavy right tail**. Model:

$$
D \;\sim\; \pi_0\, G_0 \;+\; (1-\pi_0)\, F_+ ,
$$

where $G_0$ is the on-time/early component (support $\le 15$ min, say) and $F_+$ is a positive, right-skewed distribution. For the strategy only the extreme tail of $F_+$ matters: we need $\Pr(D \ge 180)$, i.e., the ~98th–99.5th percentile. **Fitting the whole body and reading off the tail is malpractice** — body-dominated MLE for a log-normal or Weibull systematically mis-estimates the 3h exceedance. Use extreme-value theory directly on the tail.

### 2.2 Candidate parametric tails

- **Log-normal**: $\ln T \sim \mathcal N(\mu, \sigma^2)$ for positive delays $T$. Classic in the flight-delay literature; fits the body well, tail often too thin for major-disruption days. Exceedance: $\Pr(T > t) = 1 - \Phi\!\left(\frac{\ln t - \mu}{\sigma}\right)$. Example: $\mu = 3.0, \sigma = 1.0$ (median 20 min, mean ≈ 33 min positive delay) gives $\Pr(T > 180) = 1 - \Phi(2.19) \approx 1.4\%$ _conditional on being late_; times $(1-\pi_0) = 0.45$ → unconditional ≈ 0.65%.
- **Weibull**: $\Pr(T>t) = \exp(-(t/\lambda)^k)$ with $k < 1$ (decreasing hazard: a flight already 1h late is _more_ likely to slip further — consistent with rotation cascades and crew-duty-time blowups). Tail still exponential-class; usually too thin at 3h.
- **Generalized Pareto (GPD) via peaks-over-threshold (POT)** — the right tool. Pickands–Balkema–de Haan: for a broad class of $F_+$, excesses over a high threshold $u$ converge to GPD:

$$
\Pr(D - u > y \mid D > u) \;=\; \left(1 + \frac{\xi y}{\sigma_u}\right)^{-1/\xi}, \qquad y > 0,\ \xi \ne 0 .
$$

Then

$$
\boxed{\;\Pr(D > 180) \;=\; \Pr(D > u)\,\left(1 + \frac{\xi\,(180-u)}{\sigma_u}\right)^{-1/\xi}\;}
$$

with $\Pr(D > u)$ estimated empirically (it's not extreme). **Worked fit** (representative LCC evening-rotation cell): $u = 60$ min, $\hat\Pr(D>60) = 6\%$, $\hat\xi = 0.4$ (heavy tail, finite mean, infinite variance region starts at $\xi \ge 0.5$), $\hat\sigma_u = 45$:

$$
\Pr(D>180 \mid D>60) = \left(1 + \frac{0.4 \times 120}{45}\right)^{-2.5} = (2.067)^{-2.5} \approx 0.163
\;\Rightarrow\; \Pr(D>180) \approx 0.98\%.
$$

Sensitivity to $\xi$ is severe (holding $\sigma_u = 45$ fixed): $\xi = 0.2 \Rightarrow \Pr(D>180|D>60) \approx 0.12$; $\xi = 0.6 \Rightarrow \approx 0.20$ — and wider still once $\sigma_u$ is re-fit per $\xi$. **Report the profile-likelihood CI on $\xi$ and propagate it into the EV CI** — tail-index uncertainty alone spans a ±2× band on $p_{\text{delay}}$, which dwarfs most other modeling choices.

- Empirical literature (US on-time data, European Eurocontrol/CODA analyses) finds shifted power-law and exponentially-truncated power-law forms for total and propagated delay — i.e., genuinely heavy tails, supporting $\xi > 0$ and the POT approach over log-normal extrapolation.
- **Three EVT caveats specific to this data.** (i) CAA punctuality files are _binned_ (delay bands), so GPD fits require the flight-level Eurocontrol R&D / OpenSky data — an explicit pipeline dependency. (ii) POT assumes approximately independent exceedances; rotation cascades violate this badly — **decluster** (runs method) or apply an extremal-index correction. (iii) The tail is a mixture of regimes (normal ops vs meltdown days): a single GPD fits a $\xi$ that averages a thin claimable tail with a fat exempt tail — the wrong object given §3.3. Fit GPD **separately on cause-filtered exceedances** where cause codes permit. Also note the far tail is truncated: delays beyond ~5–8h become cancellations (duty-time cliff), so treat the GPD upper endpoint accordingly.

### 2.3 Delay propagation and the rotation effect

The dominant _predictable_ structure is **reactionary delay through aircraft rotations**. A single narrow-body flies 4–8 legs/day (Wizz/Ryanair schedule ~11–13 block-hours with 25–35 min turnarounds). Delay propagates via a **Lindley-type recursion** (identical in form to G/G/1 queue waiting time):

$$
d_k \;=\; \max\!\big(0,\; a_{k-1} - s_k\big) + \varepsilon_k, \qquad a_k = d_k + \eta_k,
$$

where $d_k, a_k$ = departure/arrival delay of leg $k$, $s_k$ = scheduled turnaround slack (buffer above minimum turn time), $\varepsilon_k \ge 0$ = new ground delay (boarding, ATC slot, technical), $\eta_k$ = en-route deviation (can be negative: pilots recover ~5–15 min airborne on short sectors).

Consequences:

- **Stochastic dominance in rotation index.** If slack $s_k$ is insufficient to absorb typical $a_{k-1}$ (true for ultra-LCC schedules by design), then $a_k \succeq_{\text{st}} a_{k-1}$ pointwise in the tail: the last rotation of the day first-order stochastically dominates the first in delay. Empirically, ≥3h delay probability on the final evening leg of a busy LCC tail is commonly **3–6×** the morning leg's. **Rotation index (leg-of-day) and scheduled departure hour are the two most powerful covariates available at booking time.**
- **Markov rotation model.** Discretize delay into states $\{0\text{–}15, 15\text{–}30, \dots, 165\text{–}180, 180+\}$ (make $180{+}$ absorbing for the payoff calc). Leg-specific transition matrices $P_k$ (estimable from tail-number-linked historical rotations; ADS-B/registration data links legs) give
  $$
  \Pr(a_K \ge 180) \;=\; e_0^\top \Big(\textstyle\prod_{k=1}^{K} P_k\Big)\, \mathbf{1}_{\{180+\}} .
  $$
  This is the cleanest generative model: it produces the full delay distribution of _your_ leg conditional on where it sits in the rotation, and it lets you condition on the morning's realized state on day-of-travel (irrelevant for booking, useful for validating the model).
- **Duty-time cliff.** Crew flight-duty-period limits create a nonlinearity: a 2h delay late in the day can become a 12h delay/cancellation when the crew times out. This fattens the far tail exactly at the 3h boundary — good for $p_{\text{delay}}$, and (crew planning being within carrier control) often good for $p_e$ too.

### 2.4 Predictive model: covariates and framing

Frame as **binary classification** of $Y = \mathbf{1}\{D \ge 180\}$ per flight, using **only booking-time-available covariates** (§4.1):

| Covariate                                                             | Known at booking?                                                                | Signal                                                        |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Airline × route × airport-pair congestion class                       | ✓                                                                                | strong, stable                                                |
| Scheduled departure hour                                              | ✓                                                                                | strong (delay hazard rises monotonically through the day)     |
| Rotation index / inferrable position in tail's day (from schedule)    | ✓ (from published schedules/history)                                             | strong                                                        |
| Scheduled turnaround slack of upstream legs                           | ✓                                                                                | strong                                                        |
| Month/season, day-of-week, holiday-peak flags                         | ✓                                                                                | moderate                                                      |
| Airport slot-coordination level, historical ATFM regulation frequency | ✓                                                                                | moderate                                                      |
| ATC strike calendar (announced)                                       | partly (strikes announced days–weeks ahead; fares are cheapest 4–10 weeks ahead) | high when available — **but strike delays are exempt** (§3.3) |
| Weather forecast                                                      | ✗ beyond ~10 days                                                                | unusable at cheap-booking horizon, and mostly exempt anyway   |
| Carrier's trailing 90-day OTP, fleet-age/subfleet reliability         | ✓                                                                                | moderate                                                      |

Models: start with **regularized logistic regression** (interpretable, well-calibrated by construction under correct specification), benchmark with **gradient boosting** (LightGBM/XGBoost) for interactions (hour × airport × season). Class imbalance (~1–2% positives) → use proper scoring, not accuracy; downsample negatives with weight correction or just fit on full data.

**Calibration is the entire game.** The decision rule is "buy iff $\hat p_{\text{delay}} \cdot \hat p_e \cdot \hat p_\pi > (c+\phi)/K_{\text{net}}$" — a _probability threshold_, not a ranking. AUC is nearly irrelevant; you need $\hat p$ to be _right in level_ at the extreme tail of its own distribution:

- **Brier score** $\text{BS} = \frac1n\sum (\hat p_i - y_i)^2$ with Murphy decomposition $\text{BS} = \text{Reliability} - \text{Resolution} + \text{Uncertainty}$; you want reliability ≈ 0 in the top prediction deciles.
- **Reliability diagrams** with quantile bins concentrated in the top 5% of $\hat p$; wide binomial CIs are unavoidable (few positives) — use isotonic recalibration or Platt scaling on a held-out fold, and prefer _pooled-over-time_ reliability at the traded threshold.
- **Skill vs. climatology:** the base-rate-by-cell model (airline × route × hour × month empirical rate, shrunk via empirical Bayes / hierarchical partial pooling) is a strong baseline. If GBM doesn't beat shrunken cell means out-of-time on Brier, it's fitting noise.

**Edge definition.** For flight $i$:

$$
\text{edge}_i \;=\; \hat p_i \;-\; \frac{c_i + \phi}{(1-\alpha)K_i} \;=\; \hat p_i - p_i^\* .
$$

Positive-edge flights are those where your calibrated probability exceeds the fare-implied breakeven. Everything in §§3–4 conditions on trading only $\text{edge}_i > 0$. **Hypothesis (untested):** after frictions, the set $\{\,i : \text{edge}_i > 0\,\}$ is nearly empty and concentrated in sub-€10 promotional fares on €400-band routes — the backtest confirms or refutes this.

---

## 3. Portfolio construction and Kelly sizing

### 3.1 Kelly fraction — derivation

Model one flight as a binary bet: stake $c$ (the fare) returns $K$ (net compensation, use $K_{\text{net}}$ in practice) with probability $p$, else $0$. Per euro staked, the win pays odds

$$
b \;=\; \frac{K - c}{c}
$$

(you gain $K - c$ on a stake of $c$), and a loss forfeits the stake. Betting bankroll fraction $f$, log-wealth growth:

$$
g(f) \;=\; p \ln(1 + f b) + (1-p)\ln(1 - f) .
$$

$$
g'(f) = \frac{p b}{1 + f b} - \frac{1-p}{1-f} = 0
\;\Longrightarrow\;
p b (1-f) = (1-p)(1 + f b)
\;\Longrightarrow\;
f\, b = pb - (1-p)
$$

$$
\boxed{\; f^\* \;=\; p - \frac{1-p}{b} \;=\; \frac{pb - (1-p)}{b} \;=\; \frac{p(K-c) - (1-p)c}{K - c} \;=\; \frac{pK - c}{K - c} \;}
$$

Sanity checks: $f^\* = 0$ exactly at breakeven $p = c/K$; $f^\* \to p$ as $K/c \to \infty$ (long-odds limit: never stake more than the win probability); $f^\* < 0$ (don't bet) whenever EV < 0 — which, per §1, is the generic case.

**Numerical example.** Suppose (optimistically) a calibrated $\hat p = 15\%$ on a $c = €25, K_{\text{net}} = €250$ flight. Then $f^\* = (0.15 \times 250 - 25)/(250 - 25) = 12.5/225 \approx \mathbf{5.6\%}$ of bankroll per flight. Half-Kelly (~2.8%) is appropriate given that $\hat p$ carries huge estimation error — Kelly with an overestimated $p$ is _over_-betting, and for long-odds bets the growth penalty for overbetting is brutally asymmetric ($g(f)$ falls off a cliff past $f^\*$ because losses hit with probability $1-p \approx 0.85$ and compound). A useful rule for lottery-type bets: with parameter uncertainty $p \sim \text{posterior}$, Kelly on $\mathbb{E}[p]$ overbets; shade toward Kelly on a lower quantile of the posterior.

### 3.2 Mean, variance, Sharpe of an $n$-flight book

Single flight (ignore $\phi$ for moments; it shifts the mean only): $X_i = K\mathbf 1_i - c$,

$$
\mu = pK - c, \qquad \sigma^2 = K^2 p(1-p), \qquad \text{SR}_1 = \frac{pK - c}{K\sqrt{p(1-p)}} .
$$

For $p$ small, $\sigma \approx K\sqrt p$: e.g., $p = 0.10, K = 250, c = 25$ (exactly breakeven): $\mu = 0$; at $p = 0.15$: $\mu = €12.5$, $\sigma = 250\sqrt{0.1275} \approx €89$, $\text{SR}_1 \approx 0.14$ **per flight**. Skewness of $X$ is $\frac{1-2p}{\sqrt{p(1-p)}} \approx +2.0$ at $p = 0.15$ — strongly positive skew, long droughts punctuated by wins.

Independent flights: $\text{SR}_n = \sqrt n \, \text{SR}_1$ — you'd need $n \approx 50$ flights to reach SR ≈ 1 _per campaign_ even at the fantastical $\hat p = 15\%$. At a realistic-but-edge-positive $\hat p = 5\%$ on $c = €10, K = €400$: $\mu = €10$, $\sigma = 400\sqrt{0.0475} \approx €87$, $\text{SR}_1 \approx 0.11$; and each unit of $n$ costs a day of flying.

**Correlation.** With pairwise payoff correlation $\rho$ (same-day, same-airport, same-weather-system flights):

$$
\text{Var}\Big(\sum X_i\Big) = n\sigma^2\big(1 + (n-1)\rho\big), \qquad \text{SR}_n = \frac{n\mu}{\sigma\sqrt{n(1+(n-1)\rho)}} \;\xrightarrow{n\to\infty}\; \frac{\mu}{\sigma\sqrt\rho} .
$$

Correlation caps the achievable Sharpe regardless of $n$. Naively, delay clustering looks _good_ for a compensation buyer — one ATC strike pays your whole book at once. The next subsection explains why that intuition is exactly wrong.

### 3.3 The adverse-selection core: the correlated tail is the exempt tail

Decompose the ≥3h delay event by cause with a one-factor structure. Let $Z$ be a systemic disruption factor (weather system, ATC/ATFM regulation, third-party strike, airport closure) and $\epsilon_i$ idiosyncratic carrier-attributable shocks (technical fault, crew shortage, airline's own ops failure, knock-on rotation mess of _its own_ making):

$$
\Pr(\text{delay}_i) = \underbrace{q_S(Z)}_{\text{systemic, exempt}} + \underbrace{q_I}_{\text{idiosyncratic, claimable}}, \qquad
\text{eligible}_i \approx \mathbf 1\{\text{cause} = I\} .
$$

Empirical cause mix for _long_ (≥3h) delays skews systemic: Eurocontrol/CODA attributes the majority of primary delay minutes in bad years to ATFM (ATC capacity/staffing/weather) regulations, and long delays disproportionately so. Take $w = \Pr(\text{systemic} \mid D \ge 180) \approx 0.5\text{–}0.65$, hence $p_e = 1 - w \approx 0.35\text{–}0.5$ on average. But the split is state-dependent:

- **Normal days:** delays are mostly rotation/technical/crew → $p_e^{\text{normal}} \approx 0.6\text{–}0.8$, but $p_{\text{delay}}^{\text{normal}}$ is small (say 0.5–1%).
- **Systemic days** ($Z$ large — the days that produce delay _clusters_ across your book): $p_{\text{delay}}^{\text{sys}}$ can be 10–30%, but $p_e^{\text{sys}} \approx 0.05\text{–}0.15$ (nearly everything is exempt, and carriers blanket-deny citing extraordinary circumstances, further slashing $p_\pi$ on those days).

Implications, quantified:

1. **Payment events are nearly idiosyncratic.** Payoff indicator $\Pi_i = \mathbf 1\{\text{delay}_i, \text{cause } I, \text{paid}\}$. Since the common factor $Z$ drives mostly exempt delays, $\text{Cov}(\Pi_i, \Pi_j)$ is far smaller than $\text{Cov}(\text{delay}_i, \text{delay}_j)$. Conditioning on payment _strips the common factor_. Numerically: if delay correlation on co-located flights is $\rho_{\text{delay}} \approx 0.3$ but 85% of the co-movement loads on exempt causes, effective payoff correlation is $\rho_\Pi \sim 0.05$. Good for variance (diversification survives), **catastrophic for expectation**: the fat systemic tail you can _see_ in historical delay data does not pay.
2. **Historical $p_{\text{delay}}$ overstates claimable probability more in exactly the cells that screen well.** Congested-airport evening slots look attractive on raw 3h+ frequency, but a large share of that frequency is ATFM-regulation-driven (exempt). A model trained on $Y = \mathbf 1\{D \ge 180\}$ and shrunk to $p$ by a _constant_ $p_e p_\pi$ will systematically overbuy systemic-delay-prone cells. **Train on the paid-claim-proxy label where possible** (cause-coded delay data: Eurocontrol CODA cause codes, carrier IATA delay codes 41–46 = technical → claimable, 71–77/81–84 = weather/ATFM → exempt), or fit a two-part model $\hat p = \hat p_{\text{delay}} \times \hat p_e(\text{covariates})$ with $\hat p_e$ _decreasing_ in the same congestion/season covariates that increase $\hat p_{\text{delay}}$.
3. **No cat-bond upside.** A portfolio designed to harvest correlated tail events (buy 20 tickets out of one airport ahead of a forecast storm/strike) collects €0 × 20 by construction — the exemption is a short position in exactly the correlated tail you tried to buy. The instrument is anti-designed for systemic harvesting: what remains harvestable is a thin stream of independent technical/crew failures, i.e., a diversifiable but tiny $q_I \cdot p_\pi \cdot K$ premium against fare cost $c$. One nuance with sign in the strategy's favor: _reactionary_ delay following a systemic trigger is not automatically exempt — carriers must show they took reasonable measures, and knock-on delays the next day are frequently claimable. This softens (but does not reverse) the adverse selection; it also concentrates the residual edge in "day-after-disruption" flights, which **cannot be targeted weeks ahead at booking time**.

### 3.4 Sizing under the realistic parameterization

At the assumed $p \approx 1\%$, $c = €25$, $K_{\text{net}} = €162.5$ (agency): $f^\* = (1.625 - 25)/137.5 < 0$ — **Kelly says the correct position is zero**. The strategy only enters Kelly-positive territory in the promotional-fare corner, where capacity (§4.5), not bankroll, binds; Kelly sizing is then academic — you take every positive-edge seat you can find and the constraint is deal flow, not risk.

---

## 4. Backtesting methodology

### 4.1 Point-in-time discipline

The cardinal sin is lookahead. Define the **information set at booking**, $\mathcal F_{t_b}$, where $t_b$ = booking time — for cheap fares, typically **3–10 weeks before departure** (LCC fares are near-monotonically increasing in the final weeks). Everything in the feature vector must be $\mathcal F_{t_b}$-measurable:

- ✅ Schedules, historical delay/cause statistics up to $t_b$, seasonal patterns, published slot regulations, _announced_ strike calendars.
- ❌ Weather forecasts (worthless at 3–10 weeks; using realized or short-horizon weather in a backtest is the classic inflation of this strategy's apparent edge — and doubly fake because weather delays are exempt anyway).
- ❌ Day-of-travel rotation state (morning leg's realized delay). Available only if you buy day-of — when fares are 3–10× more expensive, moving $p^\*$ out of reach. **There is a fare-information tradeoff frontier: information about $D$ arrives on exactly the timescale over which $c$ rises.** A rigorous treatment models $c(t)$ as an increasing (stochastic) function of $t \to t_{\text{dep}}$ and asks whether $\partial (pK)/\partial t$ ever exceeds $\partial c/\partial t$ — empirically it does not, except possibly in the final hours before a visibly melting-down operation (where same-day fares occasionally lag the delay news; this "delay-sniping" variant is the only sub-strategy with a plausible information edge, and it's capacity-tiny and increasingly priced by airlines' dynamic fare engines).

### 4.2 Data requirements

1. **Fare-at-booking panel** — the hard one. Historical _offered fares_ by flight × booking-date (GDS snapshots, ATPCO data, or self-scraped LCC fare histories). Without it you cannot compute historical edge $\hat p_i - p_i^\*$; using average fares biases the backtest because cheap-fare availability correlates with load factor, which correlates with congestion and season, which correlate with $p_{\text{delay}}$ and $p_e$.
2. **Flight status history with tail numbers** (for rotation features): Eurocontrol R&D archive, OpenSky/ADS-B, FlightAware/Flightradar24 historical, national CAA on-time data.
3. **Cause codes**: Eurocontrol CODA delay-cause aggregates; carrier IATA delay codes where obtainable; claim-outcome data (agency datasets, court/NEB statistics) to calibrate $p_e, p_\pi$.
4. **Strike/disruption calendar** with announcement dates (point-in-time!).

### 4.3 Validation protocol

- **Walk-forward (rolling-origin) validation**: train on years $[T-3, T)$, trade year $T$, roll. Never k-fold across time — delay regimes are strongly non-stationary (post-2022 European ATC capacity crisis roughly doubled ATFM delays vs. 2015; a model trained through 2019 is miscalibrated by ~2× in 2024–2026).
- **Blocked/clustered resampling** for CIs: bootstrap **days** (or airport-days), not flights, to respect delay-cluster correlation; report bootstrap CIs on total P&L, hit rate, and calibration at the traded threshold.
- **Biases to kill:**
  - _Rotation-index look-ahead_ (the subtlest leak, on the strongest covariate): tail assignments are not published 3–10 weeks out. Using realized rotation position from historical ADS-B is look-ahead; the backtest must reconstruct rotation index as inferable **from the published schedule alone** at the simulated booking date, and accept re-fleeting/re-timing noise.
  - _Calibration leakage_: isotonic/Platt recalibration must be fit on a **nested out-of-time** fold inside the walk-forward loop, never on pooled future data.
  - _Publication lag_: trailing cell base rates must be as-of the **data-availability date** (CAA publishes ~2–3 months in arrears), not the period end.
  - _Effective-threshold uncertainty_: arrival is doors-open (C-452/13) but on-block/touchdown fields understate it by 5–10 min (favorable), while airlines fight the 2h55–3h05 boundary (unfavorable). Run the label threshold as a 170–190 min sensitivity band, not a point.
  - _Survivorship/selection in delay stats_: published OTP tables condition on operated flights and surviving routes/carriers; heavily disrupted routes get cut, biasing historical cell means downward for continuing routes and making dead awful cells invisible. Build stats from the full historical schedule, not from currently-marketed routes.
  - _Cancellation censoring_: a would-be 5h delay often becomes a cancellation; treat cancellation <14d as a (different-payoff) positive, not a missing value.
  - _Denominator gaming_: diverted/returned flights, schedule changes between booking and departure (retiming can void your targeted rotation position).
  - _Claim-outcome selection_: agency success-rate stats condition on claims the agency _accepted_ (they pre-screen for eligibility) — do not use "98% success" marketing numbers as $p_\pi$; those are $\Pr(\text{paid} \mid \text{agency took the case})$.

### 4.4 Transaction costs and frictions — explicit ledger

| Item                          | Magnitude                                                   | Notes                                                                                                            |
| ----------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Agency commission             | 25–35% of $K$ (+VAT)                                        | AirHelp/Flightright-class; legal-action tier up to ~50%                                                          |
| DIY claim time                | 0.5–3h (filing → NEB complaint → small claims)              | denial-first is standard carrier strategy                                                                        |
| Denial/litigation drag        | $p_\pi \approx 0.75\text{–}0.9$; 3–18 months to cash        | discount for time value + hassle                                                                                 |
| Payment friction              | card FX fees, LCC extras (seat/bag traps), airport transfer | €3–15/flight; realistic all-in $c$ runs €10–20 above headline promo fares — enough to erase the Example C corner |
| Schedule-change kill          | re-timing/cancellation >14d out voids the selected rotation | ~3–10% of months-ahead LCC bookings → refund only, EV resets to ~−φ                                              |
| Time to/at airport            | 4–8h per attempt                                            | at even €10/h this alone exceeds most fares                                                                      |
| Tail risk of the trade itself | you're in Bucharest on a Tuesday                            | re-positioning cost home is a _second fare_ unless the return leg is itself part of the book                     |

### 4.5 Capacity

Positive-edge inventory = (number of flights in worst-decile $p$ cells) × (promo-fare seats per flight, typically 5–20 seats in the deepest fare bucket) × (fraction bookable before the bucket closes). Under the placeholder parameters, a single-person operation might find **a few dozen positive-edge seats per year** in the sub-€10, $K = €400$ corner — gross expected profit per seat of order €5–15 (see Example C), annual expected gross in the low hundreds of euros pre-time-cost. If that holds up empirically, the edge does not scale — measure it, don't assume it.

### 4.6 Proposed pipeline

```
[1] Ingest: schedules + tail-linked status history + CODA causes + fare snapshots + strike calendar
[2] Point-in-time feature builder (asof-joins keyed on booking_date):
      cell base rates (shrunken), rotation index, upstream slack, hour, season,
      airport ATFM-regulation propensity, carrier reliability, announced strikes
[3] Labels: y_delay = 1{D>=180}; y_claimable = y_delay & cause in claimable codes
[4] Models: hierarchical cell-mean baseline -> logistic -> GBM; two-part p̂ = p̂_delay × p̂_e(x)
[5] Calibration: isotonic on out-of-time fold; reliability at traded threshold; Brier decomposition
[6] Strategy sim: for each historical booking date, buy iff p̂·(1-α)K > c_offered + φ,
      respecting fare-bucket capacity; apply p_π, payment lags, cost ledger (§4.4)
[7] Evaluation: walk-forward P&L; day-blocked bootstrap CIs; drought analysis
      (max drawdown in flights, P(no win in n) = (1-p)^n — at p=2%, 50 flights: 36% chance of zero wins)
[8] Kill criteria: edge CI includes 0 after frictions -> stop
```

---

## 5. Worked examples — **illustrative only**

Throughout: $\mathbb{E}[X] = p\,(1-\alpha)K - c - \phi$; $p = p_{\text{delay}} \cdot p_e \cdot p_\pi$.

> **Every input below ($p_{\text{delay}}$, $p_e$, $p_\pi$, fares) is an assumed placeholder,
> chosen to show how the EV machinery responds to inputs. No cell has been measured yet; the
> pipeline will re-run these examples with estimated parameters.**

### Example A — Typical "cheap LCC short-haul" (the trade most people imagine)

Stansted→Dublin-class route, ~450 km ⇒ $K = €250$. Evening rotation, congested origin. $c = €19.99$, DIY ($\alpha = 0$), $\phi = €10$ (claim admin only; travel time charitably ignored).

- $p_{\text{delay}} = 2.8\%$ (a genuinely bad cell — fleet median is nearer 1%)
- $p_e = 0.45$, $p_\pi = 0.85$ ⇒ $p = 0.028 \times 0.45 \times 0.85 = 1.07\%$

$$
\mathbb{E}[X] = 0.0107 \times 250 - 19.99 - 10 = 2.68 - 29.99 = \mathbf{-€27.3}.
$$

Required $p^\* = 29.99/250 = 12.0\%$ vs. achieved 1.07% — short by **11.2×**. Even at $p_e = p_\pi = 1$ (fantasy), EV $= 0.028 \times 250 - 30 = -€23$.

### Example B — "Cherry-picked worst cell" with agency claiming

Slot-constrained hub, last rotation, August, carrier in operational meltdown regime. $c = €29$, $K = €400$ (2,000 km route), agency $\alpha = 0.35$, $\phi = €5$.

- $p_{\text{delay}} = 6\%$ (99th-percentile cell) — but high _because_ of ATFM/weather exposure, so eligibility is _below_ average: $p_e = 0.30$; agency handles enforcement: $p_\pi = 0.9$
- $p = 0.06 \times 0.30 \times 0.9 = 1.62\%$

$$
\mathbb{E}[X] = 0.0162 \times 0.65 \times 400 - 29 - 5 = 4.21 - 34 = \mathbf{-€29.8}.
$$

Note the §3.3 effect in action: more than doubling $p_{\text{delay}}$ vs. Example A (2.14×) bought only a 1.5× increase in $p$ because the incremental delays are exempt-cause-loaded. Breakeven would need $p^\* = 34/260 = 13.1\%$.

### Example C — The only corner that can go green: promo fare, €400 band, claimable-cause cell

Flash-sale $c = €7.99$ on a 1,900 km route ⇒ $K = €400$. Cell chosen for _idiosyncratic_ (technical/rotation) delay propensity, not congestion: mid-tier uncongested airports, old subfleet, last rotation. DIY, $\phi = €8$.

- $p_{\text{delay}} = 3.5\%$, and because the cell's delays are mostly carrier-attributable: $p_e = 0.65$, $p_\pi = 0.85$
- $p = 0.035 \times 0.65 \times 0.85 = 1.93\%$

$$
\mathbb{E}[X] = 0.0193 \times 400 - 7.99 - 8 = 7.74 - 15.99 = \mathbf{-€8.3}.
$$

Still negative under these assumed inputs. Push to the very corner — $c = €5$, $\phi = €5$ (ruthless efficiency), same $p$: EV $= 7.74 - 10 = \mathbf{-€2.3}$. To get EV $= +€5$ you need $p \approx 3.7\%$, i.e., $p_{\text{delay}} \approx 6.7\%$ _of claimable-cause type_. **Whether any real cell reaches that is exactly what the pipeline must measure** — under these placeholder assumptions the EV>0 set would be tiny, with single-digit-euro profit per seat and a 96%+ chance any given ticket returns −$c$.

### Sensitivity table — $\mathbb{E}[X]$ (€) vs. $p$ and $c$, at $K_{\text{net}} = 250$, $\phi = 0$

$\mathbb{E}[X] = 250p - c$; bold = EV > 0.

| $p$ ↓ \ $c$ → |        €5 |       €10 |       €20 |      €30 |   €40 |   €50 |
| ------------: | --------: | --------: | --------: | -------: | ----: | ----: |
|          0.5% |      −3.8 |      −8.8 |     −18.8 |    −28.8 | −38.8 | −48.8 |
|            1% |      −2.5 |      −7.5 |     −17.5 |    −27.5 | −37.5 | −47.5 |
|            2% |       0.0 |      −5.0 |     −15.0 |    −25.0 | −35.0 | −45.0 |
|            3% |  **+2.5** |      −2.5 |     −12.5 |    −22.5 | −32.5 | −42.5 |
|            5% |  **+7.5** |  **+2.5** |      −7.5 |    −17.5 | −27.5 | −37.5 |
|            8% | **+15.0** | **+10.0** |       0.0 |    −10.0 | −20.0 | −30.0 |
|           10% | **+20.0** | **+15.0** |  **+5.0** |     −5.0 | −15.0 | −25.0 |
|           15% | **+32.5** | **+27.5** | **+17.5** | **+7.5** |  −2.5 | −12.5 |

Same grid at $K_{\text{net}} = 400$: $\mathbb{E}[X] = 400p - c$ — the EV>0 boundary shifts to $p^\* = c/400$ (e.g., 2.5% at $c=€10$), which is why every realistic construction routes through the €400 distance band. Under this document's placeholder constructions, collected-$p$ tops out near **2%** — where real cells land is unmeasured.

---

## 6. Analogues and market efficiency

### 6.1 Flight-delay insurance is the market print for $p$

Parametric delay insurance (embedded card benefits, OTA add-ons, parametric insurtechs of the Blink/former-Fizzy type, AirHelp+ style subscriptions) pays $B$ automatically at a delay threshold for premium $\pi_{\text{prem}}$. Standard pricing $\pi_{\text{prem}} = \frac{p_{\text{ins}} B}{1 - L}$ with load $L \approx 0.3\text{–}0.5$ inverts to a **market-implied delay probability**:

$$
p_{\text{ins}} = \frac{\pi_{\text{prem}}(1 - L)}{B}.
$$

Typical prints (order of magnitude: €5–8 premium for €100 at 3h+) imply $p_{\text{ins}} \approx 2.5\text{–}5\%$ _for all-cause delay_ — insurers pay regardless of extraordinary circumstances, so $p_{\text{ins}}$ is an _upper_ bound on the claimable EU261 probability for comparable flights. The market that professionally prices this exact risk, with better data than any retail modeler, marks it at 2–5% all-cause — consistent with our §1–2 estimates and roughly **3–8× below** the frictioned breakeven $p^\* \approx 16\text{–}19\%$ at typical fares. (Caveat on the inference: insurance premiums price the _average_ customer's organic trip mix plus load, not a cherry-picked cell — the bound is on the average, so a selected cell exceeding it does not contradict the insurer's book.) If flights with claimable-$p$ ≈ 10–15% existed in size, delay insurers (who quote per-flight, dynamically, using the same covariates) would be un-writable on those flights; instead they simply price up or exclude them — evidence the tail is watched.

### 6.2 Where the strategy sits in the taxonomy of skew bets

- **Insurance-linked securities / cat bonds, inverted:** you are _long_ catastrophe. But unlike a cat bond investor, your correlated-catastrophe payoff is voided by the exemption clause (§3.3) — you hold a cat bond whose trigger excludes catastrophes. What's left is closer to buying **idiosyncratic default protection** on single names (technical failures) at a spread set by fare economics that ignore the protection entirely.
- **Lottery/longshot markets:** longshot bias (overpriced low-$p$ bets) is the documented norm in betting markets; here the "price" $c$ isn't set by bettors at all, which cuts both ways — no bias to harvest, but also no mechanism forcing $c$ up on high-$p$ flights. The edge, if any, is an _ignored-covariate_ edge, not a behavioral one.
- **AirHelp/Flightright as the real arbitrageurs:** the claim agencies run the profitable version of this trade — they buy _already-realized_ claims (conditional on delay having occurred, $p_{\text{delay}} = 1$, only $p_e p_\pi$ risk remains) at a 25–35% discount, with zero fare cost and legal-scale enforcement. Several also run outright **claim purchasing** (instant cash for assignment of the claim) — pricing $p_e p_\pi$ per claim. That market's existence confirms the _post-delay_ claim is valuable and priceable, and simultaneously explains why the _pre-delay_ ticket is not: all the option value sits in the delay event itself, which no one sells cheap. The airline, in turn, prices expected EU261 outlay into its network cost base (ERA/A4E put it at ~€5 per passenger-segment industry-wide; older/LCC-specific estimates €1–3 per passenger) — the liability is socialized across all fares rather than loaded onto risky flights, which is precisely the mispricing this strategy tries to exploit and precisely why it's too small to clear frictions: **the per-seat mispricing is bounded by the airline's own per-seat EU261 cost, i.e., a few euros.** You cannot extract more than a few euros of expectation from an instrument whose issuer only leaks a few euros of expectation on it, no matter how well you select — selection concentrates the leak but the leak is small.

### 6.3 Working hypothesis (pre-data — to be tested, not asserted)

$$
\text{EV} > 0 \iff \hat p > \frac{c + \phi}{(1-\alpha)K}
\quad\text{with (assumed)}\quad
\hat p \lesssim 2\%,\;\; p^\* \gtrsim 12\text{–}19\% \text{ at normal cheap fares}
$$

(the 12% end is the bare $c=€20/K=€250$ case with minimal friction, Example A; the headline €25/€250 case with realistic friction is 16–19%).

**Hypothesis:** the strategy is a negative-EV lottery outside a small corner (sub-€10 fares, €400 band, idiosyncratic-cause cells) where EV per seat is single-digit euros and the time cost of actually flying erases the residue. The pipeline tests this against measured $\hat p_{\text{delay}}$ and cause-coded eligibility. Regardless of the outcome, the _durable_ products are (a) the delay-probability model itself — valuable as a claim-overlay optimizer for travel you'd take anyway ($v_{\text{trip}} > 0$ makes the overlay strictly free money), and as a claim-purchasing pricer; and (b) the calibration/backtest framework, which is exactly the machinery a delay insurer or claim agency runs.

---

## References and data sources

- Regulation (EC) No 261/2004; CJEU: _Sturgeon_ C-402/07, _Nelson_ C-581/10, _Wallentin-Hermann_ C-549/07, _van der Lans_ C-257/14, _Pešková_ C-315/15, _Krüsemann_ C-195/17.
- Delay propagation and distribution literature: [Jetzki, "The propagation of air transport delays in Europe" (Eurocontrol/RWTH thesis)](https://www.eurocontrol.int/sites/default/files/2020-06/propagation-delays-2009.pdf); [Fleurquin, Ramasco, Eguíluz, "Systemic delay propagation in the US airport network," Sci. Rep. 3:1159 (2013)](https://www.nature.com/articles/srep01159); [Li et al., "A Review of Research on Flight Delay Propagation," J. Adv. Transportation (2025)](https://onlinelibrary.wiley.com/doi/full/10.1155/atr/4851103) (shifted power-law / truncated power-law delay distributions); [US on-time performance tail analyses (arXiv:1304.2528)](https://arxiv.org/pdf/1304.2528); [rotation-chain propagation features for delay prediction (arXiv:2605.07364)](https://arxiv.org/pdf/2605.07364); [delay-absorption capability modeling (arXiv:2512.08197)](https://arxiv.org/pdf/2512.08197).
- Operational statistics: Eurocontrol CODA delay-cause digests; [IATA on European ATC delay doubling over the last decade](https://www.iata.org/en/pressroom/2025-releases/2025-12-09-03/); carrier disruption rankings (claim-agency marketing — treat as upper bounds on "disruption," not on 3h+ delay): [flightrights.net airline ranking](https://flightrights.net/en/blog/airline-ranking/), [myflyright delay/cancellation rankings](https://myflyright.com/blog/top-european-airlines-with-delays-and-cancellations/), [SkyRefund most-delayed airports](https://skyrefund.com/en/blog/most-delayed-airports-europe).
- EVT: Pickands (1975); Balkema & de Haan (1974); Coles, _An Introduction to Statistical Modeling of Extreme Values_ (2001), ch. 4 (POT/GPD).
- Kelly (1956), "A New Interpretation of Information Rate"; Thorp (2006), "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market."
- Calibration: Murphy (1973) Brier decomposition; Niculescu-Mizil & Caruana (2005) on GBM calibration.
