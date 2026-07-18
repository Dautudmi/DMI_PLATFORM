from apps.portfolio.models.holding import Holding
from apps.portfolio.models.position_analysis import PositionAnalysis
from apps.portfolio.services.position_analyzer import PositionAnalyzer


def test_position_analyzer_returns_position_analysis():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = PositionAnalyzer()
    result = analyzer.analyze(holding)

    assert isinstance(result, PositionAnalysis)


def test_position_analyzer_calculates_market_value():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = PositionAnalyzer()
    result = analyzer.analyze(holding)

    assert result.market_value == 10000000


def test_position_analyzer_calculates_cost_value():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = PositionAnalyzer()
    result = analyzer.analyze(holding)

    assert result.cost_value == 8000000


def test_position_analyzer_calculates_unrealized_pnl():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = PositionAnalyzer()
    result = analyzer.analyze(holding)

    assert result.unrealized_pnl == 2000000


def test_position_analyzer_calculates_unrealized_return():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = PositionAnalyzer()
    result = analyzer.analyze(holding)

    assert result.unrealized_return == 0.25


def test_position_analyzer_handles_missing_current_price():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=None,
    )

    analyzer = PositionAnalyzer()
    result = analyzer.analyze(holding)

    assert result.market_value == 0.0
    assert result.cost_value == 8000000
    assert result.unrealized_pnl == 0.0
    assert result.unrealized_return == 0.0


def test_position_analyzer_rejects_invalid_input():
    analyzer = PositionAnalyzer()

    try:
        analyzer.analyze("not a holding")
    except TypeError as exc:
        assert "Holding" in str(exc)
    else:
        assert False