from dmi_core.decision.decision_confidence_calculator import (
    DecisionConfidenceCalculator,
)
from dmi_core.decision.decision_policy import DecisionPolicy
from dmi_core.decision.decision_result import DecisionResult
from dmi_core.decision.rules.base_rule import DecisionRule
from dmi_core.models.financial_analysis_result import FinancialAnalysisResult
from dmi_core.valuation.valuation_result import ValuationResult


class SellRule(DecisionRule):

    def __init__(self):
        self._calculator = DecisionConfidenceCalculator()

    def evaluate(
        self,
        analysis: FinancialAnalysisResult,
        valuation: ValuationResult,
        policy: DecisionPolicy,
    ) -> DecisionResult | None:

        confidence = self._calculator.calculate(
            analysis,
            valuation,
        )

        return DecisionResult(
            recommendation="SELL",
            confidence=confidence,
            stars=2,
            summary="Financial quality is below the investment threshold.",
            reasons=[],
            risks=[
                "Financial score is low.",
            ],
        )