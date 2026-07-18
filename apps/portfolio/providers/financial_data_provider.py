from abc import ABC, abstractmethod

from dmi_core.models.financial_statement import FinancialStatement


class FinancialDataProvider(ABC):
    """
    Abstract boundary for financial statement data access.

    Implementations may load data from CSV, database, API, cache, or mock data.
    """

    @abstractmethod
    def get_statement(self, symbol: str) -> FinancialStatement | None:
        """
        Return the latest FinancialStatement for a stock symbol.

        Returns None if no financial data is available.
        """
        raise NotImplementedError