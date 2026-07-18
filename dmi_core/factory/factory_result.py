from __future__ import annotations

from dataclasses import dataclass, field

from dmi_core.models.financial_statement import (
    FinancialStatement,
)


@dataclass(slots=True)
class FactoryResult:
    """
    Result returned by FinancialStatementFactory.

    The factory never raises validation errors for ordinary
    data issues. Instead, it returns a FactoryResult
    containing:

    - constructed FinancialStatement (if possible)
    - warnings
    - errors
    """

    statement: FinancialStatement | None = None

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    errors: tuple[str, ...] = field(
        default_factory=tuple
    )

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

    def explain(
        self,
    ) -> str:

        lines = []

        lines.append(
            "Financial Statement Factory"
        )

        lines.append(
            f"Success: {self.succeeded}"
        )

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")

            for item in self.warnings:
                lines.append(
                    f"- {item}"
                )

        if self.errors:
            lines.append("")
            lines.append("Errors:")

            for item in self.errors:
                lines.append(
                    f"- {item}"
                )

        return "\n".join(lines)