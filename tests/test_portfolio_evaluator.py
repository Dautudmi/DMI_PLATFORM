from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio

from dmi_core.health import HealthLevel
from dmi_core.portfolio import PortfolioEvaluator


def test_portfolio_evaluator_runs_complete_pipeline():

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

    evaluator = PortfolioEvaluator()

    evaluation = evaluator.evaluate(portfolio)

    assert evaluation.metrics.total_value == 36_000_000
    assert evaluation.health.level in (
    HealthLevel.GOOD,
    HealthLevel.FAIR,
    )
    assert len(evaluation.insights) >= 1
    assert evaluation.summary.startswith("Portfolio Health")
    assert evaluation.portfolio.client_name == "Demo"


def test_portfolio_evaluator_handles_empty_portfolio():

    portfolio = Portfolio(
        client_name="Empty",
        cash=0,
        holdings=[],
    )

    evaluator = PortfolioEvaluator()

    evaluation = evaluator.evaluate(portfolio)

    assert evaluation.metrics.total_value == 0
    assert evaluation.health.level == HealthLevel.CRITICAL