from __future__ import annotations

from dmi_core.factory.factory_result import (
    FactoryResult,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.providers.provider_result import (
    ProviderResult,
)


def create_statement() -> FinancialStatement:
    return FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        provider="CafeF",
    )


def test_provider_result_success() -> None:
    statement = create_statement()

    result = ProviderResult(
        statement=statement,
        provider_name="CafeFProvider",
        symbol="FPT",
        period="NAM",
        page_size=4,
    )

    assert result.succeeded is True
    assert result.has_warning is False
    assert result.has_error is False
    assert result.statement is statement


def test_provider_result_with_warning_still_succeeds() -> None:
    result = ProviderResult(
        statement=create_statement(),
        warnings=(
            "Quarter mismatch.",
        ),
        provider_name="CafeFProvider",
        symbol="FPT",
    )

    assert result.succeeded is True
    assert result.has_warning is True
    assert result.has_error is False


def test_provider_result_with_error_fails() -> None:
    result = ProviderResult(
        statement=None,
        errors=(
            "Provider failed.",
        ),
        provider_name="CafeFProvider",
        symbol="FPT",
    )

    assert result.succeeded is False
    assert result.has_warning is False
    assert result.has_error is True


def test_provider_result_with_statement_and_error_fails() -> None:
    result = ProviderResult(
        statement=create_statement(),
        errors=(
            "Mapping error.",
        ),
    )

    assert result.succeeded is False
    assert result.has_error is True


def test_provider_result_without_statement_fails() -> None:
    result = ProviderResult()

    assert result.succeeded is False


def test_normalized_symbol() -> None:
    result = ProviderResult(
        symbol="  fpt  ",
    )

    assert result.normalized_symbol == "FPT"


def test_normalized_symbol_none() -> None:
    result = ProviderResult(
        symbol=None,
    )

    assert result.normalized_symbol is None


def test_normalized_symbol_empty_returns_none() -> None:
    result = ProviderResult(
        symbol="   ",
    )

    assert result.normalized_symbol is None


def test_provider_result_keeps_factory_result() -> None:
    statement = create_statement()

    factory_result = FactoryResult(
        statement=statement,
    )

    result = ProviderResult(
        statement=statement,
        factory_result=factory_result,
    )

    assert result.factory_result is factory_result


def test_provider_result_preserves_metadata() -> None:
    result = ProviderResult(
        statement=create_statement(),
        provider_name="TEST",
        symbol="fpt",
        period="QUY",
        page_size=8,
        source="DMI-PROVIDER",
        schema_version="1.1",
    )

    assert result.provider_name == "TEST"
    assert result.normalized_symbol == "FPT"
    assert result.period == "QUY"
    assert result.page_size == 8
    assert result.source == "DMI-PROVIDER"
    assert result.schema_version == "1.1"


def test_explain_success() -> None:
    result = ProviderResult(
        statement=create_statement(),
        provider_name="CafeFProvider",
        symbol="fpt",
        period="NAM",
        page_size=4,
    )

    explanation = result.explain()

    assert "Financial Statement Provider" in explanation
    assert "Provider: CafeFProvider" in explanation
    assert "Symbol: FPT" in explanation
    assert "Period: NAM" in explanation
    assert "Page Size: 4" in explanation
    assert "Success: True" in explanation


def test_explain_warning() -> None:
    result = ProviderResult(
        statement=create_statement(),
        warnings=(
            "Quarter mismatch.",
        ),
    )

    explanation = result.explain()

    assert "Warnings:" in explanation
    assert "- Quarter mismatch." in explanation


def test_explain_error() -> None:
    result = ProviderResult(
        errors=(
            "ConnectionError: API unavailable",
        ),
    )

    explanation = result.explain()

    assert "Errors:" in explanation

    assert (
        "- ConnectionError: API unavailable"
        in explanation
    )