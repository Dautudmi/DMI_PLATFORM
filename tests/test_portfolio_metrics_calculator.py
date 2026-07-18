from dmi_core.portfolio import PortfolioMetricsCalculator

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio


def test_calculate_metrics():

    portfolio = Portfolio(
        client_name="Demo",
        cash=20_000_000,
        holdings=[
            Holding(
                symbol="FPT",
                quantity=100,
                average_cost=80_000,
                current_price=100_000,
            ),
            Holding(
                symbol="MBB",
                quantity=200,
                average_cost=25_000,
                current_price=30_000,
            ),
        ],
    )

    calculator = PortfolioMetricsCalculator()

    metrics = calculator.calculate(portfolio)

    assert metrics.total_value == 36_000_000
    assert metrics.cash_value == 20_000_000
    assert metrics.number_of_holdings == 2
    assert metrics.cash_weight > 0
    assert metrics.largest_position_weight > 0


def test_empty_portfolio():

    portfolio = Portfolio(
        client_name="Demo",
        cash=0,
        holdings=[],
    )

    calculator = PortfolioMetricsCalculator()

    metrics = calculator.calculate(portfolio)

    assert metrics.total_value == 0
    assert metrics.number_of_holdings == 0