from __future__ import annotations

from dataclasses import dataclass, field

from dmi_core.factory.factory_result import (
    FactoryResult,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)


@dataclass(slots=True)
class ProviderResult:
    """
    Result returned by FinancialStatementProvider.

    It contains:

    - final FinancialStatement
    - raw factory result
    - warnings
    - errors
    - provider metadata

    Ordinary provider, parsing, mapping and validation
    failures are represented as errors instead of forcing
    application code to inspect multiple exception types.
    """

    statement: FinancialStatement | None = None

    factory_result: FactoryResult | None = None

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    errors: tuple[str, ...] = field(
        default_factory=tuple
    )

    provider_name: str = "UNKNOWN"

    symbol: str | None = None

    period: str = "NAM"

    page_size: int = 4

    source: str = "DMI"

    schema_version: str = "1.0"

    @property
    def succeeded(
        self,
    ) -> bool:
        return (
            self.statement is not None
            and not self.errors
        )

    @property
    def has_warning(
        self,
    ) -> bool:
        return bool(
            self.warnings
        )

    @property
    def has_error(
        self,
    ) -> bool:
        return bool(
            self.errors
        )

    @property
    def normalized_symbol(
        self,
    ) -> str | None:
        if self.symbol is None:
            return None

        normalized = str(
            self.symbol
        ).strip().upper()

        return normalized or None

    def explain(
        self,
    ) -> str:
        lines = [
            "Financial Statement Provider",
            f"Provider: {self.provider_name}",
            (
                "Symbol: "
                f"{self.normalized_symbol or 'N/A'}"
            ),
            f"Period: {self.period}",
            f"Page Size: {self.page_size}",
            f"Success: {self.succeeded}",
        ]

        if self.warnings:
            lines.extend(
                [
                    "",
                    "Warnings:",
                ]
            )

            for warning in self.warnings:
                lines.append(
                    f"- {warning}"
                )

        if self.errors:
            lines.extend(
                [
                    "",
                    "Errors:",
                ]
            )

            for error in self.errors:
                lines.append(
                    f"- {error}"
                )

        return "\n".join(
            lines
        )