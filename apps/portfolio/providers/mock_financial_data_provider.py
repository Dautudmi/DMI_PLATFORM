from dmi_core.models.financial_statement import FinancialStatement

from apps.portfolio.providers.financial_data_provider import FinancialDataProvider


class MockFinancialDataProvider(FinancialDataProvider):
    """
    In-memory financial data provider for tests.
    """

    def __init__(
        self,
        statements: dict[str, FinancialStatement] | None = None,
    ) -> None:
        self._statements = statements or {}

    def get_statement(self, symbol: str) -> FinancialStatement | None:
        return self._statements.get(symbol)