from __future__ import annotations

import pytest

from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
)
from dmi_core.valuation.ev_ebitda_valuation import (
    EVEBITDAValuation,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)


def create_statement(
    ebitda: float | None = 500.0,
    total_debt: float | None = 1_000.0,
    cash: float | None = 500.0,
    charter_capital: float | None = 1_000.0,
) -> FinancialStatement:
    """
    Create a FinancialStatement for EV/EBITDA tests.

    Default calculation:

        Target Enterprise Value
            = EBITDA × Target EV/EBITDA
            = 500 × 8
            = 4,000

        Equity Fair Value
            = Enterprise Value - Debt + Cash
            = 4,000 - 1,000 + 500
            = 3,500

        Fair Value Per Share
            = Equity Fair Value / Charter Capital × 10,000
            = 3,500 / 1,000 × 10,000
            = 35,000 VND/share
    """

    balance_sheet = BalanceSheet(
        symbol="AAA",
        year=2025,
        quarter=4,
        total_debt=total_debt,
        cash=cash,
        charter_capital=charter_capital,
        equity=2_000.0,
    )

    income_statement = IncomeStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
        ebitda=ebitda,
    )

    return FinancialStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
    )


def test_ev_ebitda_calculates_intrinsic_value() -> None:
    statement = create_statement()

    config = ValuationConfig(
        target_ev_ebitda=8.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
        config=config,
    ).evaluate()

    assert result.method == "EVEBITDA"

    assert result.intrinsic_value == pytest.approx(
        35_000.0
    )

    assert result.current_price is None
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"

    assert result.source == config.source
    assert result.schema_version == config.schema_version


def test_ev_ebitda_returns_buy() -> None:
    statement = create_statement()

    config = ValuationConfig(
        target_ev_ebitda=8.0,
        required_margin_of_safety=0.25,
    )

    result = EVEBITDAValuation(
        statement=statement,
        config=config,
    ).evaluate(
        current_price=25_000.0,
    )

    # Intrinsic value = 35,000
    # Upside = (35,000 - 25,000) / 25,000 = 40%
    # MOS = (35,000 - 25,000) / 35,000 = 28.57%

    assert result.intrinsic_value == pytest.approx(
        35_000.0
    )

    assert result.current_price == pytest.approx(
        25_000.0
    )

    assert result.upside == pytest.approx(
        0.40
    )

    assert result.downside == pytest.approx(
        0.0
    )

    assert result.margin_of_safety == pytest.approx(
        10_000.0 / 35_000.0
    )

    assert result.recommendation == "BUY"


def test_ev_ebitda_returns_watch() -> None:
    statement = create_statement()

    config = ValuationConfig(
        target_ev_ebitda=8.0,
        required_margin_of_safety=0.25,
    )

    result = EVEBITDAValuation(
        statement=statement,
        config=config,
    ).evaluate(
        current_price=31_500.0,
    )

    # Intrinsic value = 35,000
    # MOS = (35,000 - 31,500) / 35,000 = 10%

    assert result.intrinsic_value == pytest.approx(
        35_000.0
    )

    assert result.upside == pytest.approx(
        3_500.0 / 31_500.0
    )

    assert result.downside == pytest.approx(
        0.0
    )

    assert result.margin_of_safety == pytest.approx(
        0.10
    )

    assert result.recommendation == "WATCH"


def test_ev_ebitda_returns_avoid() -> None:
    statement = create_statement()

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate(
        current_price=40_000.0,
    )

    # Intrinsic value = 35,000
    # Upside = -12.5%
    # Downside = 12.5%
    # MOS = -14.2857%

    assert result.intrinsic_value == pytest.approx(
        35_000.0
    )

    assert result.upside == pytest.approx(
        -0.125
    )

    assert result.downside == pytest.approx(
        0.125
    )

    assert result.margin_of_safety == pytest.approx(
        -5_000.0 / 35_000.0
    )

    assert result.recommendation == "AVOID"


def test_ev_ebitda_without_ebitda_returns_na() -> None:
    statement = create_statement(
        ebitda=None,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate(
        current_price=25_000.0,
    )

    assert result.method == "EVEBITDA"
    assert result.intrinsic_value is None

    assert result.current_price == pytest.approx(
        25_000.0
    )

    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_without_charter_capital_returns_na() -> None:
    statement = create_statement(
        charter_capital=None,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_with_zero_charter_capital_returns_na() -> None:
    statement = create_statement(
        charter_capital=0.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_with_negative_charter_capital_returns_na() -> None:
    statement = create_statement(
        charter_capital=-1_000.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_treats_missing_debt_as_zero() -> None:
    statement = create_statement(
        ebitda=500.0,
        total_debt=None,
        cash=500.0,
        charter_capital=1_000.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate()

    # EV = 500 × 8 = 4,000
    # Equity value = 4,000 - 0 + 500 = 4,500
    # Fair value = 4,500 / 1,000 × 10,000 = 45,000

    assert result.intrinsic_value == pytest.approx(
        45_000.0
    )


def test_ev_ebitda_treats_missing_cash_as_zero() -> None:
    statement = create_statement(
        ebitda=500.0,
        total_debt=1_000.0,
        cash=None,
        charter_capital=1_000.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate()

    # EV = 4,000
    # Equity value = 4,000 - 1,000 = 3,000
    # Fair value = 30,000

    assert result.intrinsic_value == pytest.approx(
        30_000.0
    )


def test_ev_ebitda_with_non_positive_equity_value_returns_na() -> None:
    statement = create_statement(
        ebitda=100.0,
        total_debt=1_000.0,
        cash=0.0,
        charter_capital=1_000.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate()

    # EV = 100 × 8 = 800
    # Equity value = 800 - 1,000 = -200

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_without_valid_current_price() -> None:
    statement = create_statement()

    result = EVEBITDAValuation(
        statement=statement,
    ).evaluate(
        current_price=0.0,
    )

    assert result.intrinsic_value == pytest.approx(
        35_000.0
    )

    assert result.current_price == pytest.approx(
        0.0
    )

    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_uses_custom_target_multiple() -> None:
    statement = create_statement(
        ebitda=500.0,
        total_debt=1_000.0,
        cash=500.0,
        charter_capital=1_000.0,
    )

    config = ValuationConfig(
        target_ev_ebitda=10.0,
    )

    result = EVEBITDAValuation(
        statement=statement,
        config=config,
    ).evaluate()

    # EV = 500 × 10 = 5,000
    # Equity value = 5,000 - 1,000 + 500 = 4,500
    # Fair value = 45,000

    assert result.intrinsic_value == pytest.approx(
        45_000.0
    )


def test_ev_ebitda_preserves_custom_metadata() -> None:
    statement = create_statement()

    config = ValuationConfig(
        source="DMI-EV",
        schema_version="3.1",
    )

    result = EVEBITDAValuation(
        statement=statement,
        config=config,
    ).evaluate()

    assert result.source == "DMI-EV"
    assert result.schema_version == "3.1"


def test_ev_ebitda_description_is_available() -> None:
    result = EVEBITDAValuation(
        statement=create_statement(),
    ).evaluate()

    assert result.description is not None

    assert (
        "EV/EBITDA"
        in result.description
    )