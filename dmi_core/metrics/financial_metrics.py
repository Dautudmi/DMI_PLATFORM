from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.models.metric_result import MetricResult


class FinancialMetrics:
    """
    Financial metrics calculator for DMI Platform.

    This class receives a FinancialStatement object and returns
    standardized MetricResult objects.
    """

    def __init__(self, statement: FinancialStatement):
        self.statement = statement
        self.balance_sheet = statement.balance_sheet
        self.income_statement = statement.income_statement

    @staticmethod
    def _safe_divide(
        numerator: float | None,
        denominator: float | None,
    ) -> float | None:
        if numerator is None or denominator is None:
            return None
        if denominator == 0:
            return None
        return numerator / denominator

    @staticmethod
    def _format_percent(value: float | None) -> str:
        if value is None:
            return "N/A"
        return f"{value * 100:.2f}%"

    @staticmethod
    def _format_number(value: float | None) -> str:
        if value is None:
            return "N/A"
        return f"{value:,.2f}"

    def roe(self) -> MetricResult:
        value = self._safe_divide(
            self.income_statement.net_profit,
            self.balance_sheet.equity,
        )

        return MetricResult(
            code="ROE",
            name="Return on Equity",
            value=value,
            display=self._format_percent(value),
            unit="%",
            formula="Net Profit / Equity",
            description="Measures profitability relative to shareholder equity.",
        )

    def roa(self) -> MetricResult:
        value = self._safe_divide(
            self.income_statement.net_profit,
            self.balance_sheet.total_assets,
        )

        return MetricResult(
            code="ROA",
            name="Return on Assets",
            value=value,
            display=self._format_percent(value),
            unit="%",
            formula="Net Profit / Total Assets",
            description="Measures profitability relative to total assets.",
        )

    def gross_margin(self) -> MetricResult:
        value = self._safe_divide(
            self.income_statement.gross_profit,
            self.income_statement.revenue,
        )

        return MetricResult(
            code="GROSS_MARGIN",
            name="Gross Margin",
            value=value,
            display=self._format_percent(value),
            unit="%",
            formula="Gross Profit / Revenue",
            description="Measures gross profitability from revenue.",
        )

    def net_margin(self) -> MetricResult:
        value = self._safe_divide(
            self.income_statement.net_profit,
            self.income_statement.revenue,
        )

        return MetricResult(
            code="NET_MARGIN",
            name="Net Margin",
            value=value,
            display=self._format_percent(value),
            unit="%",
            formula="Net Profit / Revenue",
            description="Measures net profitability from revenue.",
        )

    def current_ratio(self) -> MetricResult:
        current_liabilities = getattr(
            self.balance_sheet,
            "current_liabilities",
            None,
        )

        value = self._safe_divide(
            self.balance_sheet.current_assets,
            current_liabilities,
        )

        return MetricResult(
            code="CURRENT_RATIO",
            name="Current Ratio",
            value=value,
            display=self._format_number(value),
            unit="x",
            formula="Current Assets / Current Liabilities",
            description="Measures short-term liquidity.",
        )

    def debt_to_equity(self) -> MetricResult:
        value = self._safe_divide(
            self.balance_sheet.total_debt,
            self.balance_sheet.equity,
        )

        return MetricResult(
            code="DEBT_TO_EQUITY",
            name="Debt to Equity",
            value=value,
            display=self._format_number(value),
            unit="x",
            formula="Total Debt / Equity",
            description="Measures financial leverage relative to equity.",
        )

    def debt_to_assets(self) -> MetricResult:
        value = self._safe_divide(
            self.balance_sheet.total_debt,
            self.balance_sheet.total_assets,
        )

        return MetricResult(
            code="DEBT_TO_ASSETS",
            name="Debt to Assets",
            value=value,
            display=self._format_percent(value),
            unit="%",
            formula="Total Debt / Total Assets",
            description="Measures debt level relative to total assets.",
        )

    def asset_turnover(self) -> MetricResult:
        value = self._safe_divide(
            self.income_statement.revenue,
            self.balance_sheet.total_assets,
        )

        return MetricResult(
            code="ASSET_TURNOVER",
            name="Asset Turnover",
            value=value,
            display=self._format_number(value),
            unit="x",
            formula="Revenue / Total Assets",
            description="Measures how efficiently assets generate revenue.",
        )

    def eps(self) -> MetricResult:
        value = self.income_statement.eps

        return MetricResult(
            code="EPS",
            name="Earnings Per Share",
            value=value,
            display=self._format_number(value),
            unit="VND/share",
            formula="Net Profit / Shares Outstanding",
            description="Earnings per share.",
        )

    def bvps(self) -> MetricResult:
        value = None

        return MetricResult(
            code="BVPS",
            name="Book Value Per Share",
            value=value,
            display="N/A",
            unit="VND/share",
            formula="Equity / Shares Outstanding",
            description="Book value per share. Not available until shares outstanding is added.",
        )

    def all(self) -> list[MetricResult]:
        """
        Return all available financial metrics.
        """

        return [
            self.roe(),
            self.roa(),
            self.gross_margin(),
            self.net_margin(),
            self.current_ratio(),
            self.debt_to_equity(),
            self.debt_to_assets(),
            self.asset_turnover(),
            self.eps(),
            self.bvps(),
        ]