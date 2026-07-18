from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.use_cases import DailyPortfolioReportUseCase


def test_daily_portfolio_report():

    portfolio = Portfolio(
        client_name="Demo",
        cash=5_000_000,
        holdings=[
            Holding(
                symbol="FPT",
                quantity=100,
                average_cost=80_000,
                current_price=100_000,
            )
        ],
    )

    report = DailyPortfolioReportUseCase().execute(portfolio)

    assert report.client_name == "Demo"
    assert report.health_score >= 0