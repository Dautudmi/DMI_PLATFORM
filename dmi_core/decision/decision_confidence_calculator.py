from __future__ import annotations

from typing import Protocol

from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)


class ValuationConfidenceInput(Protocol):
    """
    Minimal valuation interface required by the
    confidence calculator.
    """

    margin_of_safety: float | None


class DecisionConfidenceCalculator:
    """
    Calculate confidence score for investment decisions.

    Confidence composition:

    - Base confidence: 50 points
    - Financial quality: up to 30 points
    - Margin of Safety: up to 20 points

    Margin of Safety uses ratio format:

        0.10 = 10%
        0.20 = 20%
        0.40 = 40%
    """

    MAX_MOS_CONTRIBUTION_THRESHOLD = 0.40

    def calculate(
        self,
        analysis: FinancialAnalysisResult,
        valuation: ValuationConfidenceInput,
    ) -> int:
        score = float(
            analysis.overall_score
        )

        raw_mos = valuation.margin_of_safety

        mos = (
            float(raw_mos)
            if raw_mos is not None
            else 0.0
        )

        confidence = 50.0

        # Financial quality contributes up to 30 points.
        normalized_score = max(
            0.0,
            min(
                score,
                100.0,
            ),
        )

        confidence += (
            normalized_score / 100.0
        ) * 30.0

        # Negative MOS must not reduce confidence below
        # the contribution produced by financial quality.
        normalized_mos = max(
            0.0,
            min(
                mos,
                self.MAX_MOS_CONTRIBUTION_THRESHOLD,
            ),
        )

        confidence += (
            normalized_mos
            / self.MAX_MOS_CONTRIBUTION_THRESHOLD
            * 20.0
        )

        confidence = max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        )

        return round(
            confidence
        )