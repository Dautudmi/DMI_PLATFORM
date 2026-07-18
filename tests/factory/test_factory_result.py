from __future__ import annotations

from dmi_core.factory.factory_result import (
    FactoryResult,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)


def create_statement() -> FinancialStatement:
    return FinancialStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
    )


def test_success_result() -> None:
    result = FactoryResult(
        statement=create_statement(),
    )

    assert result.succeeded is True
    assert result.has_warning is False
    assert result.has_error is False


def test_warning_result() -> None:
    result = FactoryResult(
        statement=create_statement(),
        warnings=(
            "Quarter mismatch.",
        ),
    )

    assert result.succeeded is True
    assert result.has_warning is True
    assert result.has_error is False


def test_error_result() -> None:
    result = FactoryResult(
        errors=(
            "Symbol mismatch.",
        ),
    )

    assert result.succeeded is False
    assert result.has_error is True


def test_explain_success() -> None:
    result = FactoryResult(
        statement=create_statement(),
    )

    text = result.explain()

    assert "Success: True" in text


def test_explain_warning() -> None:
    result = FactoryResult(
        statement=create_statement(),
        warnings=("Quarter mismatch.",),
    )

    text = result.explain()

    assert "Warnings:" in text
    assert "Quarter mismatch." in text


def test_explain_error() -> None:
    result = FactoryResult(
        errors=("Year mismatch.",),
    )

    text = result.explain()

    assert "Errors:" in text
    assert "Year mismatch." in text