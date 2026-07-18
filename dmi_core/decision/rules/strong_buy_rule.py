from dmi_core.decision.decision_confidence_calculator import (
    DecisionConfidenceCalculator,
)
from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.decision.decision_result import (
    DecisionResult,
)
from dmi_core.decision.rules.base_rule import (
    DecisionRule,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


class StrongBuyRule(DecisionRule):
    """
    Return STRONG BUY when financial quality and
    Margin of Safety meet the strong-buy thresholds.

    Margin of Safety uses ratio format:

        0.15 = 15%
        0.20 = 20%
    """

    def __init__(
        self,
    ) -> None:
        self._calculator = (
            DecisionConfidenceCalculator()
        )

    def evaluate(
        self,
        analysis: FinancialAnalysisResult,
        valuation: ValuationResult,
        policy: DecisionPolicy,
    ) -> DecisionResult | None:
        score = analysis.overall_score
        mos = valuation.margin_of_safety

        if mos is None:
            return None

        if (
            score >= policy.min_score_buy
            and mos
            >= policy.min_margin_of_safety
        ):
            confidence = (
                self._calculator.calculate(
                    analysis,
                    valuation,
                )
            )

            return DecisionResult(
                recommendation="STRONG BUY",
                confidence=confidence,
                stars=policy.strong_buy_stars,
                summary=(
                    "Excellent financial quality "
                    "with attractive valuation."
                ),
                reasons=[
                    "Financial score is excellent.",
                    (
                        "Margin of Safety is "
                        "attractive."
                    ),
                ],
                risks=[],
            )

        return None