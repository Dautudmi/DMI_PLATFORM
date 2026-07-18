from dmi_core.health import (
    HealthLevel,
    HealthSummary,
    PortfolioHealth,
)


def test_portfolio_health_model():
    health = PortfolioHealth(
        score=87,
        level=HealthLevel.GOOD,
    )

    assert health.score == 87
    assert health.level == HealthLevel.GOOD
    assert health.healthy is True


def test_portfolio_health_unhealthy():
    health = PortfolioHealth(
        score=45,
        level=HealthLevel.WEAK,
    )

    assert health.healthy is False


def test_health_summary_model():
    summary = HealthSummary(
        strengths=["Diversified portfolio"],
        weaknesses=["High banking exposure"],
        opportunities=["Increase cash allocation"],
    )

    assert summary.strengths[0] == "Diversified portfolio"
    assert summary.weaknesses[0] == "High banking exposure"
    assert summary.opportunities[0] == "Increase cash allocation"