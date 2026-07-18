from dmi_core.models.financial_statement import FinancialStatement

from apps.portfolio.providers.financial_data_provider import FinancialDataProvider


class NullFinancialDataProvider(FinancialDataProvider):
    """
    Default provider used when no financial data source is configured.
    """

    def get_statement(
        self,
        symbol: str,
    ) -> FinancialStatement | None:
        return None