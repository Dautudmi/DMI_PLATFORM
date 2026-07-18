from dmi_core.health import HealthLevel, PortfolioHealth
from dmi_core.metrics import PortfolioMetrics
from dmi_core.portfolio import PortfolioInsightGenerator


def test_generate_low_cash_insight():

    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=1_000_000,
        cash_weight=0.01,
        number_of_holdings=5,
        largest_position_weight=0.20,
        concentration_ratio=0.20,
    )

    health = PortfolioHealth(
        score=80,
        level=HealthLevel.GOOD,
    )

    generator = PortfolioInsightGenerator()

    insights = generator.generate(metrics, health)

    assert len(insights) == 1
    assert insights.insights[0].title == "Low Cash Allocation"


def test_generate_concentration_insight():

    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=10_000_000,
        cash_weight=0.10,
        number_of_holdings=3,
        largest_position_weight=0.45,
        concentration_ratio=0.45,
    )

    health = PortfolioHealth(
        score=80,
        level=HealthLevel.GOOD,
    )

    generator = PortfolioInsightGenerator()

    insights = generator.generate(metrics, health)

    assert len(insights) == 1
    assert insights.insights[0].title == "Large Position"


def test_generate_excellent_health_insight():

    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=15_000_000,
        cash_weight=0.15,
        number_of_holdings=8,
        largest_position_weight=0.18,
        concentration_ratio=0.18,
    )

    health = PortfolioHealth(
        score=95,
        level=HealthLevel.EXCELLENT,
    )

    generator = PortfolioInsightGenerator()

    insights = generator.generate(metrics, health)

    assert len(insights) == 1
    assert insights.insights[0].title == "Healthy Portfolio"


def test_generate_multiple_insights():

    metrics = PortfolioMetrics(
        total_value=100_000_000,
        cash_value=1_000_000,
        cash_weight=0.01,
        number_of_holdings=2,
        largest_position_weight=0.60,
        concentration_ratio=0.60,
    )

    health = PortfolioHealth(
        score=35,
        level=HealthLevel.CRITICAL,
    )

    generator = PortfolioInsightGenerator()

    insights = generator.generate(metrics, health)

    assert len(insights) == 3
    assert insights.has_critical() is True