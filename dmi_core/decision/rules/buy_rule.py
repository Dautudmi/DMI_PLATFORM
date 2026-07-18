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


class BuyRule(DecisionRule):
    """
    Return BUY when financial quality and valuation
    meet the regular-buy thresholds.

    Margin of Safety uses ratio format:

        0.10 = 10%
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
            score
            >= policy.min_score_regular_buy
            and mos
            >= policy.min_margin_of_safety_buy
        ):
            confidence = (
                self._calculator.calculate(
                    analysis,
                    valuation,
                )
            )

            return DecisionResult(
                recommendation="BUY",
                confidence=confidence,
                stars=policy.buy_stars,
                summary=(
                    "Good financial quality with "
                    "reasonable valuation."
                ),
                reasons=[
                    "Financial score is good.",
                    "Valuation is acceptable.",
                ],
                risks=[],
            )

        return None