from __future__ import annotations

from dataclasses import dataclass

from dmi_core.decision.decision_result import (
    DecisionResult,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


@dataclass(slots=True)
class InvestmentEvaluationResult:
    """
    Aggregate result of a complete investment evaluation.

    This result combines:

    - financial analysis
    - weighted valuation
    - final investment decision

    It is the standard output of InvestmentEvaluationEngine
    and acts as the primary result object for applications such as:

    - portfolio management
    - stock screening
    - client reporting
    - Telegram reporting
    - REST API
    - broker dashboards
    """

    symbol: str

    analysis: FinancialAnalysisResult

    valuation: WeightedFairValueResult

    decision: DecisionResult

    current_price: float | None = None

    source: str = "DMI"

    schema_version: str = "1.0"

    @property
    def recommendation(
        self,
    ) -> str:
        """
        Final investment recommendation.

        Example:
            STRONG BUY
            BUY
            WATCH
            SELL
        """

        return self.decision.recommendation

    @property
    def confidence(
        self,
    ) -> int:
        """
        Final decision confidence score.
        """

        return self.decision.confidence

    @property
    def stars(
        self,
    ) -> int:
        """
        Final investment rating expressed as stars.
        """

        return self.decision.stars

    @property
    def financial_score(
        self,
    ) -> float:
        """
        Overall financial analysis score.
        """

        return self.analysis.overall_score

    @property
    def financial_rating(
        self,
    ) -> str:
        """
        Overall financial analysis rating.
        """

        return self.analysis.overall_rating

    @property
    def intrinsic_value(
        self,
    ) -> float | None:
        """
        Weighted intrinsic value.
        """

        return self.valuation.intrinsic_value

    @property
    def fair_value(
        self,
    ) -> float | None:
        """
        Alias for weighted intrinsic value.
        """

        return self.valuation.fair_value

    @property
    def upside(
        self,
    ) -> float | None:
        """
        Upside relative to the current market price.

        Ratio format:
            0.20 = 20%
        """

        return self.valuation.upside

    @property
    def downside(
        self,
    ) -> float | None:
        """
        Downside relative to the current market price.

        Ratio format:
            0.20 = 20%
        """

        return self.valuation.downside

    @property
    def margin_of_safety(
        self,
    ) -> float | None:
        """
        Weighted valuation Margin of Safety.

        Ratio format:
            0.15 = 15%
            0.25 = 25%
        """

        return self.valuation.margin_of_safety

    @property
    def valuation_method(
        self,
    ) -> str:
        """
        Name of the aggregate valuation method.
        """

        return self.valuation.method

    @property
    def valuation_component_count(
        self,
    ) -> int:
        """
        Number of valid valuation methods used to calculate
        the weighted fair value.
        """

        return self.valuation.valid_component_count

    @property
    def is_actionable(
        self,
    ) -> bool:
        """
        Whether the result contains enough information
        to support an investment action.

        A result is actionable when:

        - weighted intrinsic value is available
        - current market price is positive
        - final recommendation is not N/A
        """

        if self.intrinsic_value is None:
            return False

        if (
            self.current_price is None
            or self.current_price <= 0
        ):
            return False

        return self.recommendation.strip().upper() != "N/A"

    @property
    def is_buy_candidate(
        self,
    ) -> bool:
        """
        Whether the final decision is a buy-type recommendation.
        """

        return self.recommendation.strip().upper() in {
            "STRONG BUY",
            "BUY",
        }

    def explain(
        self,
    ) -> str:
        """
        Return a human-readable explanation of the complete
        investment evaluation.
        """

        lines = [
            f"Symbol: {self.symbol}",
            (
                "Financial Score: "
                f"{self.financial_score:.2f}"
            ),
            (
                "Financial Rating: "
                f"{self.financial_rating}"
            ),
            (
                "Weighted Fair Value: "
                f"{self._format_number(self.fair_value)}"
            ),
            (
                "Current Price: "
                f"{self._format_number(self.current_price)}"
            ),
            (
                "Margin of Safety: "
                f"{self._format_percent(self.margin_of_safety)}"
            ),
            (
                "Recommendation: "
                f"{self.recommendation}"
            ),
            (
                "Confidence: "
                f"{self.confidence}%"
            ),
            (
                "Stars: "
                f"{self.stars}"
            ),
            "",
            self.decision.explain(),
        ]

        return "\n".join(lines)

    def _format_number(
        self,
        value: float | None,
    ) -> str:
        if value is None:
            return "N/A"

        return f"{value:,.2f}"

    def _format_percent(
        self,
        value: float | None,
    ) -> str:
        if value is None:
            return "N/A"

        return f"{value * 100:.2f}%"