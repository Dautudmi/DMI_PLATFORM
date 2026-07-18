from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.report import PortfolioReport
from apps.portfolio.services.portfolio_analyzer import PortfolioAnalyzer


def test_portfolio_analyzer_returns_portfolio_report():
    portfolio = Portfolio(
        client_name="Test Client",
        cash=0,
        holdings=[
            Holding(symbol="FPT", quantity=100, average_cost=80000),
            Holding(symbol="MBB", quantity=200, average_cost=25000),
        ],
    )

    analyzer = PortfolioAnalyzer()
    report = analyzer.analyze(portfolio)

    assert isinstance(report, PortfolioReport)
    assert report.portfolio == portfolio


def test_portfolio_analyzer_returns_empty_recommendations_initially():
    portfolio = Portfolio(
        client_name="Test Client",
        cash=0,
        holdings=[
            Holding(symbol="FPT", quantity=100, average_cost=80000),
        ],
    )

    analyzer = PortfolioAnalyzer()
    report = analyzer.analyze(portfolio)

    assert report.recommendations == []


def test_portfolio_analyzer_returns_holding_analyses():
    portfolio = Portfolio(
        client_name="Test Client",
        holdings=[
            Holding(
                symbol="FPT",
                quantity=100,
                average_cost=80000,
                current_price=100000,
            ),
            Holding(
                symbol="MBB",
                quantity=200,
                average_cost=25000,
                current_price=26000,
            ),
        ],
    )

    analyzer = PortfolioAnalyzer()
    report = analyzer.analyze(portfolio)

    assert len(report.holding_analyses) == 2
    assert report.holding_analyses[0].symbol == "FPT"
    assert report.holding_analyses[0].position.market_value == 10000000
    assert report.holding_analyses[1].symbol == "MBB"
    assert report.holding_analyses[1].position.market_value == 5200000


def test_portfolio_analyzer_rejects_invalid_input():
    analyzer = PortfolioAnalyzer()

    try:
        analyzer.analyze("not a portfolio")
    except TypeError as exc:
        assert "Portfolio" in str(exc)
    else:
        assert False