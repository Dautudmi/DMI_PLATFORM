from __future__ import annotations

from dmi_core.mappers.cafef_mapper import (
    CafeFMapper,
)
from dmi_core.parsers.cafef_parser import (
    CafeFParser,
)
from dmi_core.providers.base_provider import (
    BaseProvider,
)
from dmi_core.providers.provider_result import (
    ProviderResult,
)


class FinancialStatementProvider:
    """
    Orchestrate provider, parser, mapper and factory layers.

    Flow:

        BaseProvider
            ↓
        Raw provider payloads
            ↓
        CafeFParser
            ↓
        Parsed DataFrames
            ↓
        CafeFMapper
            ↓
        FinancialStatementFactory
            ↓
        FinancialStatement

    This class does not:

    - perform financial analysis
    - perform valuation
    - make investment decisions
    """

    def __init__(
        self,
        provider: BaseProvider,
        provider_name: str | None = None,
        source: str = "DMI",
        schema_version: str = "1.0",
    ) -> None:
        if provider is None:
            raise ValueError(
                "provider must not be None"
            )

        if not isinstance(
            provider,
            BaseProvider,
        ):
            raise TypeError(
                "provider must inherit BaseProvider"
            )

        self._provider = provider

        self._provider_name = (
            self._normalize_required_text(
                value=provider_name,
                field_name="provider_name",
            )
            if provider_name is not None
            else provider.__class__.__name__
        )

        self._source = (
            self._normalize_required_text(
                value=source,
                field_name="source",
            )
        )

        self._schema_version = (
            self._normalize_required_text(
                value=schema_version,
                field_name="schema_version",
            )
        )

    @property
    def provider(
        self,
    ) -> BaseProvider:
        return self._provider

    @property
    def provider_name(
        self,
    ) -> str:
        return self._provider_name

    @property
    def source(
        self,
    ) -> str:
        return self._source

    @property
    def schema_version(
        self,
    ) -> str:
        return self._schema_version

    def get(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
        raise_on_error: bool = False,
    ) -> ProviderResult:
        """
        Build a FinancialStatement from provider data.

        Parameters
        ----------
        symbol:
            Stock symbol.

        period:
            Provider reporting period, for example:
            - NAM
            - QUY

        page_size:
            Number of periods requested from the provider.

        raise_on_error:
            When False, ordinary provider or mapping failures
            are returned inside ProviderResult.errors.

            When True, the original exception is raised.
        """

        normalized_symbol = self._normalize_symbol(
            symbol
        )

        normalized_period = self._normalize_period(
            period
        )

        normalized_page_size = (
            self._validate_page_size(
                page_size
            )
        )

        try:
            raw_balance_sheet = (
                self._provider.get_balance_sheet(
                    normalized_symbol,
                    period=normalized_period,
                    page_size=normalized_page_size,
                )
            )

            raw_income_statement = (
                self._provider.get_income_statement(
                    normalized_symbol,
                    period=normalized_period,
                    page_size=normalized_page_size,
                )
            )

            balance_df = (
                CafeFParser.parse_finance_report(
                    raw_balance_sheet
                )
            )

            income_df = (
                CafeFParser.parse_finance_report(
                    raw_income_statement
                )
            )

            normalized_balance_df = (
                CafeFMapper.normalize_finance_df(
                    balance_df
                )
            )

            normalized_income_df = (
                CafeFMapper.normalize_finance_df(
                    income_df
                )
            )

            factory_result = (
                CafeFMapper.to_factory_result(
                    balance_df=(
                        normalized_balance_df
                    ),
                    income_df=(
                        normalized_income_df
                    ),
                )
            )

            warnings = list(
                factory_result.warnings
            )

            errors = list(
                factory_result.errors
            )

            if (
                factory_result.statement
                is None
                and not errors
            ):
                errors.append(
                    "Financial statement could not "
                    "be constructed."
                )

            return ProviderResult(
                statement=(
                    factory_result.statement
                ),
                factory_result=factory_result,
                warnings=tuple(
                    warnings
                ),
                errors=tuple(
                    errors
                ),
                provider_name=(
                    self._provider_name
                ),
                symbol=normalized_symbol,
                period=normalized_period,
                page_size=normalized_page_size,
                source=self._source,
                schema_version=(
                    self._schema_version
                ),
            )

        except Exception as exc:
            if raise_on_error:
                raise

            return ProviderResult(
                statement=None,
                factory_result=None,
                warnings=(),
                errors=(
                    (
                        f"{exc.__class__.__name__}: "
                        f"{exc}"
                    ),
                ),
                provider_name=(
                    self._provider_name
                ),
                symbol=normalized_symbol,
                period=normalized_period,
                page_size=normalized_page_size,
                source=self._source,
                schema_version=(
                    self._schema_version
                ),
            )

    def _normalize_symbol(
        self,
        symbol: str,
    ) -> str:
        return self._normalize_required_text(
            value=symbol,
            field_name="symbol",
        ).upper()

    def _normalize_period(
        self,
        period: str,
    ) -> str:
        return self._normalize_required_text(
            value=period,
            field_name="period",
        ).upper()

    def _validate_page_size(
        self,
        page_size: int,
    ) -> int:
        if isinstance(
            page_size,
            bool,
        ):
            raise TypeError(
                "page_size must be an integer"
            )

        if not isinstance(
            page_size,
            int,
        ):
            raise TypeError(
                "page_size must be an integer"
            )

        if page_size <= 0:
            raise ValueError(
                "page_size must be greater than zero"
            )

        return page_size

    def _normalize_required_text(
        self,
        value: object,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized = str(
            value
        ).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized