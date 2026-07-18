from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.portfolio_insight import PortfolioInsight
from apps.portfolio.models.portfolio_intelligence_report import (
    PortfolioIntelligenceReport,
)


def test_portfolio_insight_model():
    insight = PortfolioInsight(
        category="allocation",
        title="High concentration",
        message="Portfolio is highly concentrated in one sector.",
        severity="warning",
    )

    assert insight.category == "allocation"
    assert insight.title == "High concentration"
    assert insight.severity == "warning"


def test_portfolio_intelligence_report_model():
    portfolio = Portfolio(
        client_name="Test Client",
        cash=10000000,
    )

    insight = PortfolioInsight(
        category="cash",
        title="High cash allocation",
        message="Client has high cash allocation.",
    )

    report = PortfolioIntelligenceReport(
        portfolio=portfolio,
        insights=[insight],
    )

    assert report.portfolio == portfolio
    assert len(report.insights) == 1
    assert report.insights[0].category == "cash"
    assert report.recommendations == []
    assert isinstance(report.summary, dict)