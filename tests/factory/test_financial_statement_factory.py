from __future__ import annotations

from dmi_core.factory.financial_statement_factory import (
    FinancialStatementFactory,
)
from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.free_cash_flow import (
    FreeCashFlow,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
)


def create_balance(
    symbol="AAA",
    year=2025,
    quarter=4,
):
    return BalanceSheet(
        symbol=symbol,
        year=year,
        quarter=quarter,
    )


def create_income(
    symbol="AAA",
    year=2025,
    quarter=4,
):
    return IncomeStatement(
        symbol=symbol,
        year=year,
        quarter=quarter,
    )


def create_cashflow(
    symbol="AAA",
    year=2025,
    quarter=4,
):
    return FreeCashFlow(
        symbol=symbol,
        year=year,
        quarter=quarter,
    )


def test_build_full_statement() -> None:
    factory = FinancialStatementFactory()

    result = factory.build(
        balance_sheet=create_balance(),
        income_statement=create_income(),
        free_cash_flow=create_cashflow(),
    )

    assert result.succeeded

    statement = result.statement

    assert statement is not None

    assert statement.symbol == "AAA"
    assert statement.year == 2025
    assert statement.quarter == 4

    assert statement.balance_sheet is not None
    assert statement.income_statement is not None
    assert statement.free_cash_flow is not None


def test_build_without_cashflow() -> None:
    factory = FinancialStatementFactory()

    result = factory.build(
        balance_sheet=create_balance(),
        income_statement=create_income(),
    )

    assert result.succeeded

    assert (
        result.statement.free_cash_flow
        is None
    )


def test_build_only_balance_sheet() -> None:
    factory = FinancialStatementFactory()

    result = factory.build(
        balance_sheet=create_balance(),
    )

    assert result.succeeded

    assert (
        result.statement.balance_sheet
        is not None
    )


def test_reject_empty_input() -> None:
    factory = FinancialStatementFactory()

    result = factory.build()

    assert result.succeeded is False

    assert (
        "No financial model supplied."
        in result.errors
    )


def test_detect_symbol_mismatch() -> None:
    factory = FinancialStatementFactory()

    result = factory.build(
        balance_sheet=create_balance(
            symbol="AAA",
        ),
        income_statement=create_income(
            symbol="BBB",
        ),
    )

    assert result.succeeded is False

    assert (
        "Symbol mismatch."
        in result.errors
    )


def test_detect_year_mismatch() -> None:
    factory = FinancialStatementFactory()

    result = factory.build(
        balance_sheet=create_balance(
            year=2025,
        ),
        income_statement=create_income(
            year=2024,
        ),
    )

    assert result.succeeded is False

    assert (
        "Year mismatch."
        in result.errors
    )


def test_detect_quarter_warning() -> None:
    factory = FinancialStatementFactory()

    result = factory.build(
        balance_sheet=create_balance(
            quarter=4,
        ),
        income_statement=create_income(
            quarter=3,
        ),
    )

    assert result.succeeded

    assert result.has_warning

    assert (
        "Quarter mismatch."
        in result.warnings
    )


def test_factory_keeps_models() -> None:
    bs = create_balance()
    ins = create_income()
    cf = create_cashflow()

    result = (
        FinancialStatementFactory()
        .build(
            balance_sheet=bs,
            income_statement=ins,
            free_cash_flow=cf,
        )
    )

    statement = result.statement

    assert statement.balance_sheet is bs
    assert statement.income_statement is ins
    assert statement.free_cash_flow is cf