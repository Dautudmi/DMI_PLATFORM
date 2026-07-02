from dmi_core.dictionary.financial_fields import CAFEF_NAME_TO_DMI_CODE
import pandas as pd

from dmi_core.models.balance_sheet import BalanceSheet
from dmi_core.models.income_statement import IncomeStatement
from dmi_core.models.financial_statement import FinancialStatement




class CafeFMapper:
    @staticmethod
    def normalize_finance_df(df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result["metric"] = result["name"].map(CAFEF_NAME_TO_DMI_CODE)
        result = result[result["metric"].notna()].copy()

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
    def to_wide_format(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()

        wide = df.pivot_table(
            index=["year", "quarter"],
            columns="metric",
            values="value",
            aggfunc="first",
        ).reset_index()

        wide.columns.name = None
        return wide

    @staticmethod
    def to_balance_sheet(df: pd.DataFrame) -> BalanceSheet | None:
        if df.empty:
            return None

        wide = CafeFMapper.to_wide_format(df)
        if wide.empty:
            return None

        row = wide.sort_values(["year", "quarter"], ascending=[False, False]).iloc[0]
        meta = df.iloc[0]

        return BalanceSheet(
            symbol=meta.get("symbol"),
            year=int(row.get("year")),
            quarter=int(row.get("quarter")),
            report_type=meta.get("report_type"),
            unit=meta.get("unit"),
            provider="CafeF",
            current_assets=row.get("current_assets"),
            total_assets=row.get("total_assets"),
            total_debt=row.get("total_debt"),
            equity=row.get("equity"),
        )

    @staticmethod
    def to_income_statement(df: pd.DataFrame) -> IncomeStatement | None:
        if df.empty:
            return None

        wide = CafeFMapper.to_wide_format(df)
        if wide.empty:
            return None

        row = wide.sort_values(["year", "quarter"], ascending=[False, False]).iloc[0]
        meta = df.iloc[0]

        return IncomeStatement(
            symbol=meta.get("symbol"),
            year=int(row.get("year")),
            quarter=int(row.get("quarter")),
            report_type=meta.get("report_type"),
            unit=meta.get("unit"),
            provider="CafeF",
            revenue=row.get("revenue"),
            cost_of_goods_sold=row.get("cost_of_goods_sold"),
            gross_profit=row.get("gross_profit"),
            pre_tax_profit=row.get("profit_before_tax"),
            net_profit=row.get("net_profit"),
        )

    @staticmethod
    def to_financial_statement(
        balance_df: pd.DataFrame,
        income_df: pd.DataFrame,
    ) -> FinancialStatement | None:
        balance_sheet = CafeFMapper.to_balance_sheet(balance_df)
        income_statement = CafeFMapper.to_income_statement(income_df)

        if balance_sheet is None and income_statement is None:
            return None

        base = balance_sheet or income_statement

        return FinancialStatement(
            symbol=base.symbol,
            year=base.year,
            quarter=base.quarter,
            balance_sheet=balance_sheet,
            income_statement=income_statement,
            report_type=base.report_type,
            unit=base.unit,
            provider="CafeF",
        )