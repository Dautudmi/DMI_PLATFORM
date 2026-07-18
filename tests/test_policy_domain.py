from dmi_core.policies import PortfolioPolicy, RiskProfile


def test_default_portfolio_policy_is_balanced():
    policy = PortfolioPolicy()

    assert policy.risk_profile == RiskProfile.BALANCED
    assert policy.max_single_position == 0.25
    assert policy.max_sector_weight == 0.35
    assert policy.min_cash == 0.05
    assert policy.max_cash == 0.30
    assert policy.target_beta == 1.0


def test_conservative_policy():
    policy = PortfolioPolicy.conservative()

    assert policy.risk_profile == RiskProfile.CONSERVATIVE
    assert policy.max_single_position == 0.15
    assert policy.max_sector_weight == 0.25
    assert policy.min_cash == 0.15
    assert policy.max_cash == 0.45
    assert policy.target_beta == 0.8


def test_aggressive_policy():
    policy = PortfolioPolicy.aggressive()

    assert policy.risk_profile == RiskProfile.AGGRESSIVE
    assert policy.max_single_position == 0.40
    assert policy.max_sector_weight == 0.55
    assert policy.min_cash == 0.00
    assert policy.max_cash == 0.20
    assert policy.target_beta == 1.3