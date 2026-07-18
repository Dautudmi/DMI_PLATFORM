import pytest

from dmi_core.models.balance_sheet import BalanceSheet
from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.models.income_statement import IncomeStatement
from dmi_core.valuation.pb_valuation import PBValuation
from dmi_core.valuation.valuation_config import ValuationConfig


def create_statement(
    equity: float | None = 2_000.0,
    charter_capital: float | None = 1_000.0,
) -> FinancialStatement:
    balance_sheet = BalanceSheet(
        symbol="AAA",
        year=2025,
        quarter=4,
        equity=equity,
        charter_capital=charter_capital,
    )

    income_statement = IncomeStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
    )

    return FinancialStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
    )


def test_pb_valuation_calculates_intrinsic_value():
    statement = create_statement(
        equity=2_000.0,
        charter_capital=1_000.0,
    )

    config = ValuationConfig(
        target_pb=1.5,
    )

    result = PBValuation(
        statement=statement,
        config=config,
    ).evaluate()

    # BVPS = 2,000 / 1,000 * 10,000 = 20,000
    # Fair value = 20,000 * 1.5 = 30,000
    assert result.method == "PB"
    assert result.intrinsic_value == pytest.approx(30_000.0)
    assert result.current_price is None
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"
    assert result.source == config.source
    assert result.schema_version == config.schema_version


def test_pb_valuation_returns_buy():
    statement = create_statement()

    config = ValuationConfig(
        target_pb=1.5,
        required_margin_of_safety=0.25,
    )

    result = PBValuation(
        statement=statement,
        config=config,
    ).evaluate(
        current_price=20_000.0,
    )

    # Intrinsic value = 30,000
    # Upside = (30,000 - 20,000) / 20,000 = 0.50
    # MOS = (30,000 - 20,000) / 30,000 = 0.3333
    assert result.intrinsic_value == pytest.approx(30_000.0)
    assert result.current_price == pytest.approx(20_000.0)
    assert result.upside == pytest.approx(0.50)
    assert result.downside == pytest.approx(0.0)
    assert result.margin_of_safety == pytest.approx(
        1 / 3
    )
    assert result.recommendation == "BUY"


def test_pb_valuation_returns_watch():
    statement = create_statement()

    config = ValuationConfig(
        target_pb=1.5,
        required_margin_of_safety=0.25,
    )

    result = PBValuation(
        statement=statement,
        config=config,
    ).evaluate(
        current_price=27_000.0,
    )

    # MOS = (30,000 - 27,000) / 30,000 = 0.10
    assert result.intrinsic_value == pytest.approx(30_000.0)
    assert result.upside == pytest.approx(
        3_000.0 / 27_000.0
    )
    assert result.downside == pytest.approx(0.0)
    assert result.margin_of_safety == pytest.approx(0.10)
    assert result.recommendation == "WATCH"


def test_pb_valuation_returns_avoid():
    statement = create_statement()

    result = PBValuation(
        statement=statement,
    ).evaluate(
        current_price=40_000.0,
    )

    # Intrinsic value = 30,000
    # Upside = -25%
    # Downside = 25%
    # MOS = -33.33%
    assert result.intrinsic_value == pytest.approx(30_000.0)
    assert result.upside == pytest.approx(-0.25)
    assert result.downside == pytest.approx(0.25)
    assert result.margin_of_safety == pytest.approx(
        -1 / 3
    )
    assert result.recommendation == "AVOID"


def test_pb_valuation_without_equity_returns_na():
    statement = create_statement(
        equity=None,
        charter_capital=1_000.0,
    )

    result = PBValuation(
        statement=statement,
    ).evaluate(
        current_price=20_000.0,
    )

    assert result.method == "PB"
    assert result.intrinsic_value is None
    assert result.current_price == pytest.approx(20_000.0)
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_pb_valuation_without_charter_capital_returns_na():
    statement = create_statement(
        equity=2_000.0,
        charter_capital=None,
    )

    result = PBValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_pb_valuation_with_zero_charter_capital_returns_na():
    statement = create_statement(
        equity=2_000.0,
        charter_capital=0.0,
    )

    result = PBValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_pb_valuation_with_negative_charter_capital_returns_na():
    statement = create_statement(
        equity=2_000.0,
        charter_capital=-1_000.0,
    )

    result = PBValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_pb_valuation_with_negative_equity_returns_na():
    statement = create_statement(
        equity=-500.0,
        charter_capital=1_000.0,
    )

    result = PBValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_pb_valuation_without_valid_current_price():
    statement = create_statement()

    result = PBValuation(
        statement=statement,
    ).evaluate(
        current_price=0.0,
    )

    assert result.intrinsic_value == pytest.approx(30_000.0)
    assert result.current_price == pytest.approx(0.0)
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_pb_valuation_uses_custom_target_pb():
    statement = create_statement(
        equity=1_500.0,
        charter_capital=1_000.0,
    )

    config = ValuationConfig(
        target_pb=2.0,
    )

    result = PBValuation(
        statement=statement,
        config=config,
    ).evaluate()

    # BVPS = 15,000
    # Fair value = 15,000 * 2 = 30,000
    assert result.intrinsic_value == pytest.approx(30_000.0)