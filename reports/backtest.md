# Phase 6 — walk-forward trading backtest

Walk-forward: trade years 2022-2025, using each cell-month's point-in-time Phase 3 shrunken-baseline prediction as the trading signal, settled against the actual realized rate (Phase 4 eligibility + Phase 5 EV engine).

## Breakeven-threshold backtest (trade iff predicted EV > £0 — the real strategy)

- **0 trades** across 2022-2025.

This is the expected, correct outcome given Phase 5's cross-sectional result (EV <= 0 in all 3,474 evaluated combinations): a walk-forward backtest of a strategy with no measured edge finds no trades. It is not a bug in the harness.

## Demonstration backtest (relaxed margin, predicted EV > £-21 — mechanics only, NOT a recommended threshold)

- Trades: 2
- Total realized EV: £-842.76 (95% bootstrap CI [£-842.76, £-842.76])
- Hit rate (bets with positive realized EV): 0.0%
- Max drawdown (cumulative realized EV path): £421.38
- Capacity: ~4,680 seats/yr across traded cells (assumes 180 seats/flight — an order-of-magnitude proxy, not measured)
- Mean annualized IRR per trade: -99.8%

## Regulatory scenario panel

| Scenario | Trades | Total realized EV | Mean IRR |
| --- | ---: | ---: | ---: |
| Current (pre-reform, 6mo DIY lag) | 2 | £-842.76 | -99.8% |
| Post-2026-reform (30-day payment, 1.5mo DIY lag) | 2 | £-842.76 | -100.0% |
| Defeated Council proposal (6h exact-band stress, same trades) | 2 | £-842.76 | n/a |

The reform doesn't change raw EV (it isn't a discount-rate model) — it only shortens payout latency. For an already-negative-EV trade this makes the *annualized* IRR look worse, not better: the same sub-1.0 money-multiple gets raised to a higher power over a shorter period. Faster payment cuts collection friction, but it does not rescue a trade with no edge. The defeated 6h-threshold stress case settles the *same* trades against a much rarer qualifying event and is uniformly worse, as expected — 4h is not computable from CAA's 121-180/181-360/>360min bands (no 240min cut point), so only the exact 6h leg of the defeated proposal is shown.
