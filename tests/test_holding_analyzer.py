from apps.portfolio.models.holding import Holding
from apps.portfolio.models.holding_analysis import HoldingAnalysis
from apps.portfolio.models.position_analysis import PositionAnalysis
from apps.portfolio.services.holding_analyzer import HoldingAnalyzer


def test_holding_analyzer_returns_holding_analysis():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = HoldingAnalyzer()
    result = analyzer.analyze(holding)

    assert isinstance(result, HoldingAnalysis)
    assert isinstance(result.position, PositionAnalysis)
    assert result.symbol == "FPT"
    assert result.quantity == 100
    assert result.average_cost == 80000
    assert result.current_price == 100000


def test_holding_analyzer_calculates_market_value():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = HoldingAnalyzer()
    result = analyzer.analyze(holding)

    assert result.position.market_value == 10000000


def test_holding_analyzer_calculates_cost_value():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = HoldingAnalyzer()
    result = analyzer.analyze(holding)

    assert result.position.cost_value == 8000000


def test_holding_analyzer_calculates_unrealized_pnl():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = HoldingAnalyzer()
    result = analyzer.analyze(holding)

    assert result.position.unrealized_pnl == 2000000


def test_holding_analyzer_calculates_unrealized_return():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    analyzer = HoldingAnalyzer()
    result = analyzer.analyze(holding)

    assert result.position.unrealized_return == 0.25


def test_holding_analyzer_handles_missing_current_price():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=None,
    )

    analyzer = HoldingAnalyzer()
    result = analyzer.analyze(holding)

    assert result.position.market_value == 0.0
    assert result.position.cost_value == 8000000
    assert result.position.unrealized_pnl == 0.0
    assert result.position.unrealized_return == 0.0


def test_holding_analyzer_rejects_invalid_input():
    analyzer = HoldingAnalyzer()

    try:
        analyzer.analyze("not a holding")
    except TypeError as exc:
        assert "Holding" in str(exc)
    else:
        assert False