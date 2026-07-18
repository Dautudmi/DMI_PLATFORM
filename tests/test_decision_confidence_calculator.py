from dmi_core.decision.decision_confidence_calculator import (
    DecisionConfidenceCalculator,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


def test_high_quality_company_has_high_confidence():

    analysis = FinancialAnalysisResult(
        overall_score=90,
    )

    valuation = ValuationResult(
        method="DCF",
        intrinsic_value=100,
        current_price=80,
        upside=25,
        downside=0,
        margin_of_safety=20,
        recommendation="BUY",
    )

    confidence = DecisionConfidenceCalculator().calculate(
        analysis,
        valuation,
    )

    assert confidence >= 85


def test_low_quality_company_has_lower_confidence():
    analysis = FinancialAnalysisResult(
        overall_score=40,
    )

    valuation = ValuationResult(
        method="DCF",
        intrinsic_value=100,
        current_price=98,
        upside=0.02,
        downside=0,
        margin_of_safety=0.02,
        recommendation="WATCH",
    )

    confidence = DecisionConfidenceCalculator().calculate(
        analysis,
        valuation,
    )

    assert confidence < 70