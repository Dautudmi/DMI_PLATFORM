from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.report import PortfolioReport, PortfolioReportBuilder
from dmi_core.portfolio import PortfolioEvaluator


def test_portfolio_report_builder_builds_report():
    portfolio = Portfolio(
        client_name="Demo",
        cash=1_000_000,
        holdings=[
            Holding(
                symbol="FPT",
                quantity=100,
                average_cost=80_000,
                current_price=100_000,
            ),
        ],
    )

    evaluation = PortfolioEvaluator().evaluate(portfolio)

    report = PortfolioReportBuilder().build(evaluation)

    assert isinstance(report, PortfolioReport)
    assert report.client_name == "Demo"
    assert report.health_score == evaluation.health.score
    assert report.health_level == evaluation.health.level.value.upper()


def test_portfolio_report_to_markdown():
    report = PortfolioReport(
        client_name="Demo",
        health_level="GOOD",
        health_score=80,
        highlights=["Cash allocation is below the preferred level."],
        suggested_actions=["Increase cash allocation."],
    )

    markdown = report.to_markdown()

    assert "# Portfolio Report - Demo" in markdown
    assert "Health: **GOOD** (80/100)" in markdown
    assert "Cash allocation is below the preferred level." in markdown
    assert "Increase cash allocation." in markdown