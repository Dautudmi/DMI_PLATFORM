from dmi_core.metrics import PortfolioMetrics


def test_portfolio_metrics_model():
    metrics = PortfolioMetrics(
        total_value=100000000,
        cash_value=20000000,
        cash_weight=0.20,
        number_of_holdings=5,
        largest_position_weight=0.30,
        concentration_ratio=0.55,
    )

    assert metrics.total_value == 100000000
    assert metrics.cash_value == 20000000
    assert metrics.cash_weight == 0.20
    assert metrics.number_of_holdings == 5
    assert metrics.largest_position_weight == 0.30
    assert metrics.concentration_ratio == 0.55


def test_portfolio_metrics_are_objective_facts():
    metrics = PortfolioMetrics(
        total_value=100000000,
        cash_value=10000000,
        cash_weight=0.10,
        number_of_holdings=3,
        largest_position_weight=0.50,
        concentration_ratio=0.80,
    )

    assert metrics.cash_weight == 0.10
    assert metrics.largest_position_weight == 0.50
    assert metrics.concentration_ratio == 0.80


def test_portfolio_metrics_allow_empty_portfolio_state():
    metrics = PortfolioMetrics(
        total_value=0.0,
        cash_value=0.0,
        cash_weight=0.0,
        number_of_holdings=0,
        largest_position_weight=0.0,
        concentration_ratio=0.0,
    )

    assert metrics.total_value == 0.0
    assert metrics.number_of_holdings == 0