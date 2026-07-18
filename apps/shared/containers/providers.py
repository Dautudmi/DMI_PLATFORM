from apps.portfolio.providers.financial_data_provider import FinancialDataProvider
from apps.portfolio.providers.null_financial_data_provider import NullFinancialDataProvider


class ProviderContainer:
    def __init__(
        self,
        financial_provider: FinancialDataProvider | None = None,
    ) -> None:
        self.financial_provider = financial_provider or NullFinancialDataProvider()