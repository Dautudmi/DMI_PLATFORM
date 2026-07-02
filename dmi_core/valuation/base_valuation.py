from abc import ABC, abstractmethod

from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.valuation.valuation_result import ValuationResult


class BaseValuation(ABC):
    """
    Base class for all valuation models in DMI Platform.

    Every valuation model must receive a FinancialStatement
    and return a ValuationResult.
    """

    def __init__(self, statement: FinancialStatement):
        self.statement = statement
        self.balance_sheet = statement.balance_sheet
        self.income_statement = statement.income_statement

    @abstractmethod
    def evaluate(
        self,
        current_price: float | None = None,
    ) -> ValuationResult:
        """
        Evaluate intrinsic value and return ValuationResult.
        """
        raise NotImplementedError