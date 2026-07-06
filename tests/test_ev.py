import pytest

from wizarb.eligibility.haircuts import p_claimable
from wizarb.ev.engine import EVParams, is_band_edge, kelly_fraction, per_bet_ev
from wizarb.ev.portfolio import simulate_portfolio


def test_per_bet_ev_breakeven_consistency():
    claim = p_claimable(p_delay=0.03, month=7, congestion_z=0.0, collection="diy")
    ev = per_bet_ev(claim, k_gbp=220.0, fare_gbp=20.0, params=EVParams(wage_per_hour=0.0))

    # At exactly the breakeven p_claimable, ev_if_completed should be ~0.
    k_net = 220.0 * claim.net_multiplier
    breakeven_ev = breakeven_claim_ev(ev.breakeven_p_claimable, k_net, ev.all_in_cost, ev.time_cost)
    assert breakeven_ev == pytest.approx(0.0, abs=1e-9)


def breakeven_claim_ev(p, k_net, cost, time_cost):
    return p * k_net - cost - time_cost


def test_per_bet_ev_schedule_kill_scales_completed_ev():
    claim = p_claimable(p_delay=0.10, month=7, congestion_z=0.0, collection="diy")
    no_kill = per_bet_ev(claim, 220.0, 20.0, EVParams(schedule_kill_prob=0.0))
    with_kill = per_bet_ev(claim, 220.0, 20.0, EVParams(schedule_kill_prob=0.2))
    assert with_kill.ev == pytest.approx(no_kill.ev_if_completed * 0.8)
    assert with_kill.ev_if_completed == pytest.approx(no_kill.ev_if_completed)


def test_kelly_fraction_bounds():
    assert kelly_fraction(p=0.001, k_net=220.0, c=30.0) == 0.0  # negative edge -> no bet
    assert kelly_fraction(p=0.9, k_net=220.0, c=30.0) > 0.0
    assert kelly_fraction(p=0.9, k_net=220.0, c=30.0) <= 1.0
    assert kelly_fraction(p=0.5, k_net=10.0, c=30.0) == 0.0  # K <= c edge case


def test_is_band_edge():
    assert is_band_edge(1490) is True  # just under 1,500km breakpoint
    assert is_band_edge(1000) is False
    assert is_band_edge(None) is False


def test_simulate_portfolio_runs_and_scores():
    result = simulate_portfolio(
        p_delay=0.03,
        month=7,
        k_gbp=220.0,
        fare_gbp=20.0,
        collection="diy",
        n_bets=40,
        bets_per_day=2,
        n_sims=100,
    )
    assert result.n_bets == 40
    assert result.n_sims == 100
    assert result.std_pnl >= 0
    assert result.ci_low <= result.mean_pnl <= result.ci_high
    assert 0.0 <= result.hit_rate <= 1.0
    assert result.mean_max_drawdown >= 0
