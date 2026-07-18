from dmi_core.health import HealthLevel
from dmi_core.metrics import PortfolioMetrics
from dmi_core.policies import PortfolioPolicy
from dmi_core.portfolio import PortfolioHealthEvaluator


def test_healthy_balanced_portfolio():
    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=15_000_000,
        cash_weight=0.15,
        number_of_holdings=5,
        largest_position_weight=0.20,
        concentration_ratio=0.30,
    )

    evaluator = PortfolioHealthEvaluator()

    health = evaluator.evaluate(
        metrics=metrics,
        policy=PortfolioPolicy.balanced(),
    )

    assert health.score == 100
    assert health.level == HealthLevel.EXCELLENT
    assert health.healthy is True


def test_low_cash_reduces_health_score():
    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=1_000_000,
        cash_weight=0.01,
        number_of_holdings=5,
        largest_position_weight=0.20,
        concentration_ratio=0.30,
    )

    evaluator = PortfolioHealthEvaluator()

    health = evaluator.evaluate(
        metrics=metrics,
        policy=PortfolioPolicy.balanced(),
    )

    assert health.score == 80
    assert health.level == HealthLevel.GOOD


def test_concentrated_position_reduces_health_score():
    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=10_000_000,
        cash_weight=0.10,
        number_of_holdings=3,
        largest_position_weight=0.50,
        concentration_ratio=0.50,
    )

    evaluator = PortfolioHealthEvaluator()

    health = evaluator.evaluate(
        metrics=metrics,
        policy=PortfolioPolicy.balanced(),
    )

    assert health.score == 55
    assert health.level == HealthLevel.WEAK


def test_empty_portfolio_is_critical():
    metrics = PortfolioMetrics(
        total_value=0,
        cash_value=0,
        cash_weight=0,
        number_of_holdings=0,
        largest_position_weight=0,
        concentration_ratio=0,
    )

    evaluator = PortfolioHealthEvaluator()

    health = evaluator.evaluate(metrics)

    assert health.score == 0
    assert health.level == HealthLevel.CRITICAL
    assert health.healthy is False