from dmi_core.decision.decision_confidence_calculator import (
    DecisionConfidenceCalculator,
)
from dmi_core.decision.decision_policy import DecisionPolicy
from dmi_core.decision.decision_result import DecisionResult
from dmi_core.decision.rules.base_rule import DecisionRule
from dmi_core.models.financial_analysis_result import FinancialAnalysisResult
from dmi_core.valuation.valuation_result import ValuationResult


class WatchRule(DecisionRule):

    def __init__(self):
        self._calculator = DecisionConfidenceCalculator()

    def evaluate(
        self,
        analysis: FinancialAnalysisResult,
        valuation: ValuationResult,
        policy: DecisionPolicy,
    ) -> DecisionResult | None:

        score = analysis.overall_score

        if score >= policy.min_score_watch:

            confidence = self._calculator.calculate(
                analysis,
                valuation,
            )

            return DecisionResult(
                recommendation="WATCH",
                confidence=confidence,
                stars=3,
                summary="Company is acceptable but not yet attractive.",
                reasons=[
                    "Financial quality is average.",
                ],
                risks=[
                    "Valuation is not attractive enough.",
                ],
            )

        return None