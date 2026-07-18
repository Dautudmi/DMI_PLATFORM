from abc import ABC, abstractmethod

from dmi_core.models.financial_analysis_result import FinancialAnalysisResult
from dmi_core.valuation.valuation_result import ValuationResult

from dmi_core.decision.decision_policy import DecisionPolicy
from dmi_core.decision.decision_result import DecisionResult


class DecisionRule(ABC):
    """
    Base class for decision rules.
    """

    @abstractmethod
    def evaluate(
        self,
        analysis: FinancialAnalysisResult,
        valuation: ValuationResult,
        policy: DecisionPolicy,
    ) -> DecisionResult | None:
        raise NotImplementedError