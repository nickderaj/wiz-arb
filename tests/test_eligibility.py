import pytest

from wizarb.eligibility.haircuts import (
    cause_mix,
    collection_outcome,
    eligibility_share,
    p_claimable,
)


def test_cause_mix_sums_to_one():
    for month in range(1, 13):
        mix = cause_mix(month)
        assert sum(mix.values()) == pytest.approx(1.0)


def test_eligibility_share_bounded_and_seasonal():
    winter = eligibility_share(1)
    summer = eligibility_share(7)
    assert 0.20 <= winter <= 0.60
    assert 0.20 <= summer <= 0.60
    # Summer's ATC/ATFM-heavy mix is more exempt than winter's weather-heavy mix.
    assert summer < winter


def test_eligibility_share_decreases_with_congestion():
    calm = eligibility_share(4, congestion_z=0.0)
    congested = eligibility_share(4, congestion_z=3.0)
    assert congested <= calm


def test_eligibility_share_clips_at_bounds():
    assert eligibility_share(4, congestion_z=100.0) == pytest.approx(0.20)
    assert eligibility_share(4, congestion_z=-100.0) == pytest.approx(0.60)


def test_collection_outcome_unknown_path_raises():
    with pytest.raises(ValueError):
        collection_outcome("cash_under_the_table")


def test_p_claimable_composition():
    result = p_claimable(p_delay=0.05, month=1, congestion_z=0.0, collection="agency")
    expected_p_e = eligibility_share(1, 0.0)
    expected_p_paid = collection_outcome("agency").p_paid
    assert result.p_claimable == pytest.approx(0.05 * expected_p_e * expected_p_paid)
    assert result.net_multiplier == pytest.approx(0.65)
    assert result.payout_lag_months == pytest.approx(3.0)
