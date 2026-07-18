from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from dmi_core.factory.factory_result import (
    FactoryResult,
)
from dmi_core.mappers.cafef_mapper import (
    CafeFMapper,
)
from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
)
from dmi_core.parsers.cafef_parser import (
    CafeFParser,
)
from dmi_core.providers.base_provider import (
    BaseProvider,
)
from dmi_core.providers.financial_statement_provider import (
    FinancialStatementProvider,
)
from dmi_core.providers.provider_result import (
    ProviderResult,
)


class FakeProvider(BaseProvider):
    """
    Fake provider used for isolated tests.

    It never makes a network request.
    """

    def __init__(
        self,
        balance_payload: Any | None = None,
        income_payload: Any | None = None,
    ) -> None:
        self.balance_payload = (
            balance_payload
            if balance_payload is not None
            else {
                "report": "balance",
            }
        )

        self.income_payload = (
            income_payload
            if income_payload is not None
            else {
                "report": "income",
            }
        )

        self.balance_calls: list[
            tuple[str, str, int]
        ] = []

        self.income_calls: list[
            tuple[str, str, int]
        ] = []

    def get_balance_sheet(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ):
        self.balance_calls.append(
            (
                symbol,
                period,
                page_size,
            )
        )

        return self.balance_payload

    def get_income_statement(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ):
        self.income_calls.append(
            (
                symbol,
                period,
                page_size,
            )
        )

        return self.income_payload


class BrokenProvider(BaseProvider):
    def get_balance_sheet(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ):
        raise ConnectionError(
            "CafeF is unavailable"
        )

    def get_income_statement(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ):
        raise AssertionError(
            "Income request should not run"
        )


class NotAProvider:
    pass


def create_statement() -> FinancialStatement:
    balance_sheet = BalanceSheet(
        symbol="FPT",
        year=2025,
        quarter=4,
        equity=10_000.0,
        total_debt=2_000.0,
        cash=1_000.0,
        charter_capital=5_000.0,
        provider="CafeF",
    )

    income_statement = IncomeStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        revenue=20_000.0,
        net_profit=3_000.0,
        eps=6_000.0,
        provider="CafeF",
    )

    return FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
        provider="CafeF",
    )


def install_success_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    statement: FinancialStatement | None = None,
    warnings: tuple[str, ...] = (),
    errors: tuple[str, ...] = (),
) -> dict[str, list[Any]]:
    """
    Replace parser and mapper functions with deterministic
    in-memory implementations.

    This keeps the test focused on orchestration performed by
    FinancialStatementProvider.
    """

    resolved_statement = (
        statement
        if statement is not None
        else create_statement()
    )

    calls: dict[
        str,
        list[Any],
    ] = {
        "parsed": [],
        "normalized": [],
        "factory": [],
    }

    def fake_parse(
        raw_payload,
    ) -> pd.DataFrame:
        calls["parsed"].append(
            raw_payload
        )

        return pd.DataFrame(
            [
                {
                    "raw": raw_payload,
                }
            ]
        )

    def fake_normalize(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        calls["normalized"].append(
            dataframe
        )

        return dataframe.assign(
            normalized=True
        )

    def fake_to_factory_result(
        balance_df: pd.DataFrame,
        income_df: pd.DataFrame,
    ) -> FactoryResult:
        calls["factory"].append(
            (
                balance_df,
                income_df,
            )
        )

        return FactoryResult(
            statement=(
                resolved_statement
                if not errors
                else None
            ),
            warnings=warnings,
            errors=errors,
        )

    monkeypatch.setattr(
        CafeFParser,
        "parse_finance_report",
        staticmethod(
            fake_parse
        ),
    )

    monkeypatch.setattr(
        CafeFMapper,
        "normalize_finance_df",
        staticmethod(
            fake_normalize
        ),
    )

    monkeypatch.setattr(
        CafeFMapper,
        "to_factory_result",
        staticmethod(
            fake_to_factory_result
        ),
    )

    return calls


def test_provider_can_be_created() -> None:
    fake_provider = FakeProvider()

    provider = FinancialStatementProvider(
        provider=fake_provider,
    )

    assert provider.provider is fake_provider
    assert provider.provider_name == "FakeProvider"
    assert provider.source == "DMI"
    assert provider.schema_version == "1.0"


def test_provider_accepts_custom_metadata() -> None:
    provider = FinancialStatementProvider(
        provider=FakeProvider(),
        provider_name="TEST-PROVIDER",
        source="DMI-TEST",
        schema_version="1.2",
    )

    assert provider.provider_name == "TEST-PROVIDER"
    assert provider.source == "DMI-TEST"
    assert provider.schema_version == "1.2"


def test_get_returns_provider_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_success_pipeline(
        monkeypatch
    )

    provider = FinancialStatementProvider(
        provider=FakeProvider(),
    )

    result = provider.get(
        symbol="FPT",
    )

    assert isinstance(
        result,
        ProviderResult,
    )

    assert result.succeeded is True


def test_get_builds_financial_statement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    statement = create_statement()

    install_success_pipeline(
        monkeypatch,
        statement=statement,
    )

    result = FinancialStatementProvider(
        provider=FakeProvider(),
    ).get(
        symbol="FPT",
    )

    assert result.statement is statement
    assert result.statement.symbol == "FPT"

    assert (
        result.statement.balance_sheet
        is not None
    )

    assert (
        result.statement.income_statement
        is not None
    )


def test_get_normalizes_symbol_and_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_success_pipeline(
        monkeypatch
    )

    fake_provider = FakeProvider()

    result = FinancialStatementProvider(
        provider=fake_provider,
    ).get(
        symbol="  fpt  ",
        period=" quy ",
        page_size=8,
    )

    assert result.normalized_symbol == "FPT"
    assert result.period == "QUY"
    assert result.page_size == 8

    assert fake_provider.balance_calls == [
        (
            "FPT",
            "QUY",
            8,
        )
    ]

    assert fake_provider.income_calls == [
        (
            "FPT",
            "QUY",
            8,
        )
    ]


def test_get_calls_parser_for_both_reports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_success_pipeline(
        monkeypatch
    )

    balance_payload = {
        "type": "BSHEET",
    }

    income_payload = {
        "type": "INSTA",
    }

    provider = FinancialStatementProvider(
        provider=FakeProvider(
            balance_payload=balance_payload,
            income_payload=income_payload,
        )
    )

    provider.get(
        symbol="FPT",
    )

    assert calls["parsed"] == [
        balance_payload,
        income_payload,
    ]


def test_get_normalizes_both_dataframes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_success_pipeline(
        monkeypatch
    )

    FinancialStatementProvider(
        provider=FakeProvider(),
    ).get(
        symbol="FPT",
    )

    assert len(
        calls["normalized"]
    ) == 2


def test_get_delegates_to_factory_mapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_success_pipeline(
        monkeypatch
    )

    FinancialStatementProvider(
        provider=FakeProvider(),
    ).get(
        symbol="FPT",
    )

    assert len(
        calls["factory"]
    ) == 1

    balance_df, income_df = (
        calls["factory"][0]
    )

    assert isinstance(
        balance_df,
        pd.DataFrame,
    )

    assert isinstance(
        income_df,
        pd.DataFrame,
    )

    assert (
        balance_df["normalized"]
        .all()
    )

    assert (
        income_df["normalized"]
        .all()
    )


def test_get_preserves_factory_warnings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_success_pipeline(
        monkeypatch,
        warnings=(
            "Quarter mismatch.",
        ),
    )

    result = FinancialStatementProvider(
        provider=FakeProvider(),
    ).get(
        symbol="FPT",
    )

    assert result.succeeded is True
    assert result.has_warning is True

    assert result.warnings == (
        "Quarter mismatch.",
    )


def test_get_preserves_factory_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_success_pipeline(
        monkeypatch,
        errors=(
            "Symbol mismatch.",
        ),
    )

    result = FinancialStatementProvider(
        provider=FakeProvider(),
    ).get(
        symbol="FPT",
    )

    assert result.succeeded is False
    assert result.statement is None
    assert result.has_error is True

    assert result.errors == (
        "Symbol mismatch.",
    )


def test_get_adds_error_when_statement_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_parse(
        raw_payload,
    ) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "raw": raw_payload,
                }
            ]
        )

    def fake_normalize(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        return dataframe

    def fake_factory(
        balance_df: pd.DataFrame,
        income_df: pd.DataFrame,
    ) -> FactoryResult:
        return FactoryResult(
            statement=None,
            warnings=(),
            errors=(),
        )

    monkeypatch.setattr(
        CafeFParser,
        "parse_finance_report",
        staticmethod(
            fake_parse
        ),
    )

    monkeypatch.setattr(
        CafeFMapper,
        "normalize_finance_df",
        staticmethod(
            fake_normalize
        ),
    )

    monkeypatch.setattr(
        CafeFMapper,
        "to_factory_result",
        staticmethod(
            fake_factory
        ),
    )

    result = FinancialStatementProvider(
        provider=FakeProvider(),
    ).get(
        symbol="FPT",
    )

    assert result.succeeded is False

    assert result.errors == (
        (
            "Financial statement could not "
            "be constructed."
        ),
    )


def test_provider_error_is_captured() -> None:
    result = FinancialStatementProvider(
        provider=BrokenProvider(),
    ).get(
        symbol="FPT",
        raise_on_error=False,
    )

    assert result.succeeded is False
    assert result.statement is None
    assert result.factory_result is None

    assert result.errors == (
        (
            "ConnectionError: "
            "CafeF is unavailable"
        ),
    )


def test_provider_error_can_be_raised() -> None:
    provider = FinancialStatementProvider(
        provider=BrokenProvider(),
    )

    with pytest.raises(
        ConnectionError,
        match="CafeF is unavailable",
    ):
        provider.get(
            symbol="FPT",
            raise_on_error=True,
        )


def test_result_preserves_provider_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_success_pipeline(
        monkeypatch
    )

    result = FinancialStatementProvider(
        provider=FakeProvider(),
        provider_name="FAKE-DATA",
        source="DMI-PRODUCTION",
        schema_version="1.3",
    ).get(
        symbol="fpt",
        period="nam",
        page_size=6,
    )

    assert result.provider_name == "FAKE-DATA"
    assert result.normalized_symbol == "FPT"
    assert result.period == "NAM"
    assert result.page_size == 6
    assert result.source == "DMI-PRODUCTION"
    assert result.schema_version == "1.3"


def test_rejects_none_provider() -> None:
    with pytest.raises(
        ValueError,
        match="provider must not be None",
    ):
        FinancialStatementProvider(
            provider=None,
        )


def test_rejects_invalid_provider_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "provider must inherit BaseProvider"
        ),
    ):
        FinancialStatementProvider(
            provider=NotAProvider(),
        )


@pytest.mark.parametrize(
    "symbol",
    [
        None,
        "",
        "   ",
    ],
)
def test_rejects_empty_symbol(
    symbol,
) -> None:
    provider = FinancialStatementProvider(
        provider=FakeProvider(),
    )

    with pytest.raises(
        ValueError,
        match="symbol must not be empty",
    ):
        provider.get(
            symbol=symbol,
        )


@pytest.mark.parametrize(
    "period",
    [
        None,
        "",
        "   ",
    ],
)
def test_rejects_empty_period(
    period,
) -> None:
    provider = FinancialStatementProvider(
        provider=FakeProvider(),
    )

    with pytest.raises(
        ValueError,
        match="period must not be empty",
    ):
        provider.get(
            symbol="FPT",
            period=period,
        )


@pytest.mark.parametrize(
    "page_size",
    [
        4.0,
        "4",
        True,
        object(),
    ],
)
def test_rejects_non_integer_page_size(
    page_size,
) -> None:
    provider = FinancialStatementProvider(
        provider=FakeProvider(),
    )

    with pytest.raises(
        TypeError,
        match="page_size must be an integer",
    ):
        provider.get(
            symbol="FPT",
            page_size=page_size,
        )


@pytest.mark.parametrize(
    "page_size",
    [
        0,
        -1,
    ],
)
def test_rejects_non_positive_page_size(
    page_size: int,
) -> None:
    provider = FinancialStatementProvider(
        provider=FakeProvider(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "page_size must be greater than zero"
        ),
    ):
        provider.get(
            symbol="FPT",
            page_size=page_size,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
        "message",
    ),
    [
        (
            "provider_name",
            "   ",
            "provider_name must not be empty",
        ),
        (
            "source",
            "",
            "source must not be empty",
        ),
        (
            "schema_version",
            " ",
            "schema_version must not be empty",
        ),
    ],
)
def test_rejects_empty_constructor_metadata(
    field_name: str,
    value: str,
    message: str,
) -> None:
    kwargs = {
        "provider": FakeProvider(),
        field_name: value,
    }

    with pytest.raises(
        ValueError,
        match=message,
    ):
        FinancialStatementProvider(
            **kwargs,
        )