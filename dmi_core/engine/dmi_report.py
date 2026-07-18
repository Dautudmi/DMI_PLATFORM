from dataclasses import dataclass

from dmi_core.models.financial_analysis_result import FinancialAnalysisResult
from dmi_core.valuation.valuation_result import ValuationResult
from dmi_core.decision.decision_result import DecisionResult


@dataclass(slots=True)
class DMIReport:
    """
    Final report object returned by DMIEngine.
    """

    symbol: str
    year: int
    quarter: int

    analysis: FinancialAnalysisResult
    valuation: ValuationResult
    decision: DecisionResult