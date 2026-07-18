from __future__ import annotations

import pandas as pd

from dmi_core.dictionary.financial_fields import (
    CAFEF_NAME_TO_DMI_CODE,
)
from dmi_core.factory.factory_result import (
    FactoryResult,
)
from dmi_core.factory.financial_statement_factory import (
    FinancialStatementFactory,
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


class CafeFMapper:
    """
    Convert normalized CafeF data into DMI domain models.

    Responsibilities:

    - normalize CafeF financial fields
    - convert normalized data into wide format
    - map data into BalanceSheet
    - map data into IncomeStatement
    - delegate FinancialStatement construction to
      FinancialStatementFactory

    The mapper does not:

    - call the CafeF API
    - parse raw JSON
    - perform financial analysis
    - perform valuation
    """

    @staticmethod
    def normalize_finance_df(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert CafeF metric names into DMI field codes.
        """

        if df is None:
            raise ValueError(
                "df must not be None"
            )

        if df.empty:
            return pd.DataFrame()

        required_columns = {
            "symbol",
            "report_title",
            "report_type",
            "type_time",
            "unit",
            "code",
            "name",
            "year",
            "quarter",
            "value",
        }

        missing_columns = (
            required_columns
            - set(df.columns)
        )

        if missing_columns:
            missing_text = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "CafeF dataframe is missing "
                f"required columns: {missing_text}"
            )

        result = df.copy()

        result["metric"] = (
            result["name"]
            .map(CAFEF_NAME_TO_DMI_CODE)
        )

        result = result[
            result["metric"].notna()
        ].copy()
        print("\n===== MAPPED METRICS =====")
        print(result[["name", "metric"]].drop_duplicates().to_string(index=False))
        print("==========================\n")

        result = result[
            [
                "symbol",
                "report_title",
                "report_type",
                "type_time",
                "unit",
                "code",
                "name",
                "metric",
                "year",
                "quarter",
                "value",
            ]
        ]

        return result

    @staticmethod
    def to_wide_format(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert normalized long-form financial data
        into one row per reporting period.
        """

        if df is None:
            raise ValueError(
                "df must not be None"
            )

        if df.empty:
            return pd.DataFrame()

        required_columns = {
            "year",
            "quarter",
            "metric",
            "value",
        }

        missing_columns = (
            required_columns
            - set(df.columns)
        )

        if missing_columns:
            missing_text = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "normalized dataframe is missing "
                f"required columns: {missing_text}"
            )

        wide = df.pivot_table(
            index=[
                "year",
                "quarter",
            ],
            columns="metric",
            values="value",
            aggfunc="first",
        ).reset_index()

        wide.columns.name = None

        return wide

    @staticmethod
    def to_balance_sheet(
        df: pd.DataFrame,
    ) -> BalanceSheet | None:
        """
        Map the latest reporting period into BalanceSheet.
        """

        if df is None:
            raise ValueError(
                "df must not be None"
            )

        if df.empty:
            return None

        wide = CafeFMapper.to_wide_format(
            df
        )

        if wide.empty:
            return None

        row = (
            wide.sort_values(
                [
                    "year",
                    "quarter",
                ],
                ascending=[
                    False,
                    False,
                ],
            )
            .iloc[0]
        )

        meta = df.iloc[0]

        return BalanceSheet(
            symbol=str(
                meta.get("symbol")
            ).strip().upper(),
            year=int(
                row.get("year")
            ),
            quarter=int(
                row.get("quarter")
            ),
            report_type=meta.get(
                "report_type"
            ),
            unit=meta.get(
                "unit"
            ) or "Billion",
            provider="CafeF",

            cash=CafeFMapper._get_value(
                row,
                "cash",
            ),
            short_term_investments=(
                CafeFMapper._get_value(
                    row,
                    "short_term_investments",
                )
            ),
            receivables=(
                CafeFMapper._get_value(
                    row,
                    "receivables",
                )
            ),
            inventory=CafeFMapper._get_value(
                row,
                "inventory",
            ),
            current_assets=(
                CafeFMapper._get_value(
                    row,
                    "current_assets",
                )
            ),
            fixed_assets=(
                CafeFMapper._get_value(
                    row,
                    "fixed_assets",
                )
            ),
            long_term_assets=(
                CafeFMapper._get_value(
                    row,
                    "long_term_assets",
                )
            ),
            total_assets=(
                CafeFMapper._get_value(
                    row,
                    "total_assets",
                )
            ),

            short_term_debt=(
                CafeFMapper._get_value(
                    row,
                    "short_term_debt",
                )
            ),
            long_term_debt=(
                CafeFMapper._get_value(
                    row,
                    "long_term_debt",
                )
            ),
            total_debt=(
                CafeFMapper._get_value(
                    row,
                    "total_debt",
                )
            ),
            total_liabilities=(
                CafeFMapper._get_value(
                    row,
                    "total_liabilities",
                )
            ),

            equity=CafeFMapper._get_value(
                row,
                "equity",
            ),
            charter_capital=(
                CafeFMapper._get_value(
                    row,
                    "charter_capital",
                )
            ),
            retained_earnings=(
                CafeFMapper._get_value(
                    row,
                    "retained_earnings",
                )
            ),
        )

    @staticmethod
    def to_income_statement(
        df: pd.DataFrame,
    ) -> IncomeStatement | None:
        """
        Map the latest reporting period into IncomeStatement.
        """

        if df is None:
            raise ValueError(
                "df must not be None"
            )

        if df.empty:
            return None

        wide = CafeFMapper.to_wide_format(
            df
        )

        if wide.empty:
            return None

        row = (
            wide.sort_values(
                [
                    "year",
                    "quarter",
                ],
                ascending=[
                    False,
                    False,
                ],
            )
            .iloc[0]
        )

        meta = df.iloc[0]

        return IncomeStatement(
            symbol=str(
                meta.get("symbol")
            ).strip().upper(),
            year=int(
                row.get("year")
            ),
            quarter=int(
                row.get("quarter")
            ),
            report_type=meta.get(
                "report_type"
            ),
            unit=meta.get(
                "unit"
            ) or "Billion",
            provider="CafeF",

            revenue=CafeFMapper._get_value(
                row,
                "revenue",
            ),
            cost_of_goods_sold=(
                CafeFMapper._get_value(
                    row,
                    "cost_of_goods_sold",
                )
            ),
            gross_profit=(
                CafeFMapper._get_value(
                    row,
                    "gross_profit",
                )
            ),

            financial_income=(
                CafeFMapper._get_value(
                    row,
                    "financial_income",
                )
            ),
            financial_expense=(
                CafeFMapper._get_value(
                    row,
                    "financial_expense",
                )
            ),
            selling_expense=(
                CafeFMapper._get_value(
                    row,
                    "selling_expense",
                )
            ),
            admin_expense=(
                CafeFMapper._get_value(
                    row,
                    "admin_expense",
                )
            ),

            operating_profit=(
                CafeFMapper._get_value(
                    row,
                    "operating_profit",
                )
            ),
            other_profit=(
                CafeFMapper._get_value(
                    row,
                    "other_profit",
                )
            ),
            pre_tax_profit=(
                CafeFMapper._first_value(
                    row,
                    "pre_tax_profit",
                    "profit_before_tax",
                )
            ),
            tax_expense=(
                CafeFMapper._get_value(
                    row,
                    "tax_expense",
                )
            ),
            net_profit=(
                CafeFMapper._get_value(
                    row,
                    "net_profit",
                )
            ),

            ebitda=CafeFMapper._get_value(
                row,
                "ebitda",
            ),
            eps=CafeFMapper._get_value(
                row,
                "eps",
            ),
        )

    @staticmethod
    def to_factory_result(
        balance_df: pd.DataFrame,
        income_df: pd.DataFrame,
    ) -> FactoryResult:
        """
        Map CafeF dataframes into domain models and delegate
        FinancialStatement construction to the factory.

        This is the preferred API for new production code.
        """

        if balance_df is None:
            raise ValueError(
                "balance_df must not be None"
            )

        if income_df is None:
            raise ValueError(
                "income_df must not be None"
            )

        balance_sheet = (
            CafeFMapper.to_balance_sheet(
                balance_df
            )
        )

        income_statement = (
            CafeFMapper.to_income_statement(
                income_df
            )
        )

        return FinancialStatementFactory().build(
            balance_sheet=balance_sheet,
            income_statement=income_statement,
        )

    @staticmethod
    def to_financial_statement(
        balance_df: pd.DataFrame,
        income_df: pd.DataFrame,
    ) -> FinancialStatement | None:
        """
        Backward-compatible FinancialStatement mapping API.

        New code should prefer:

            CafeFMapper.to_factory_result(...)

        The actual aggregate construction is delegated to
        FinancialStatementFactory.
        """

        factory_result = (
            CafeFMapper.to_factory_result(
                balance_df=balance_df,
                income_df=income_df,
            )
        )

        return factory_result.statement

    @staticmethod
    def _get_value(
        row: pd.Series,
        field_name: str,
    ) -> float | None:
        """
        Safely read a numeric value from a wide-format row.
        """

        if field_name not in row.index:
            return None

        value = row.get(
            field_name
        )

        if pd.isna(value):
            return None

        return float(
            value
        )

    @staticmethod
    def _first_value(
        row: pd.Series,
        *field_names: str,
    ) -> float | None:
        """
        Return the first available field value.
        """

        for field_name in field_names:
            value = CafeFMapper._get_value(
                row,
                field_name,
            )

            if value is not None:
                return value

        return None