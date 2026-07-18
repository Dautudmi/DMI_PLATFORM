from apps.portfolio.models import (
    Holding,
    Portfolio,
    PortfolioRecommendation,
    PortfolioReport,
)


def test_portfolio_models():

    holding = Holding(
        symbol="AAA",
        quantity=1000,
        average_cost=35,
    )

    portfolio = Portfolio(
        client_name="Nguyen Duc Manh",
    )

    portfolio.holdings.append(holding)

    recommendation = PortfolioRecommendation(
        symbol="AAA",
        action="BUY",
        confidence=95,
        reason="High quality business.",
    )

    report = PortfolioReport(
        portfolio_score=86,
        overall_risk="Medium",
        recommendations=[recommendation],
        summary="Portfolio quality is good.",
    )

    print(portfolio)
    print(report)


if __name__ == "__main__":
    test_portfolio_models()