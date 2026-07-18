from __future__ import annotations

from dmi_core.factory.factory_result import (
    FactoryResult,
)
from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.models.free_cash_flow import (
    FreeCashFlow,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
)


class FinancialStatementFactory:
    """
    Aggregate FinancialStatement from individual
    financial models.

    Responsibilities:

    - construct FinancialStatement
    - validate basic consistency
    - collect warnings/errors

    It intentionally does NOT:

    - parse raw JSON
    - download data
    - perform financial analysis
    """

    def build(
        self,
        *,
        balance_sheet: BalanceSheet | None = None,
        income_statement: IncomeStatement | None = None,
        free_cash_flow: FreeCashFlow | None = None,
    ) -> FactoryResult:

        warnings: list[str] = []
        errors: list[str] = []

        models = [
            model
            for model in (
                balance_sheet,
                income_statement,
                free_cash_flow,
            )
            if model is not None
        ]

        if not models:
            errors.append(
                "No financial model supplied."
            )

            return FactoryResult(
                statement=None,
                warnings=tuple(warnings),
                errors=tuple(errors),
            )

        symbol = models[0].symbol
        year = models[0].year
        quarter = getattr(
            models[0],
            "quarter",
            None,
        )

        for model in models[1:]:

            if model.symbol != symbol:
                errors.append(
                    "Symbol mismatch."
                )

            if model.year != year:
                errors.append(
                    "Year mismatch."
                )

            if (
                getattr(
                    model,
                    "quarter",
                    None,
                )
                != quarter
            ):
                warnings.append(
                    "Quarter mismatch."
                )

        if errors:
            return FactoryResult(
                statement=None,
                warnings=tuple(warnings),
                errors=tuple(errors),
            )

        statement = FinancialStatement(
            symbol=symbol,
            year=year,
            quarter=quarter or 0,
            balance_sheet=balance_sheet,
            income_statement=income_statement,
            free_cash_flow=free_cash_flow,
        )

        return FactoryResult(
            statement=statement,
            warnings=tuple(warnings),
            errors=tuple(errors),
        )