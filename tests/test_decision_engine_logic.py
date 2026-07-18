from dmi_core.decision import (
    DecisionEngine,
    DecisionPolicy,
)

from dmi_core.models.financial_analysis_result import FinancialAnalysisResult
from dmi_core.valuation.valuation_result import ValuationResult


def create_analysis(score: int):

    return FinancialAnalysisResult(
        profitability=None,
        leverage=None,
        liquidity=None,
        efficiency=None,
        growth=None,
        overall_score=score,
        recommendation="BUY",
    )


def create_value(mos: float):

    return ValuationResult(
        method="PE",
        intrinsic_value=100,
        current_price=80,
        upside=25,
        downside=0,
        margin_of_safety=mos,
        recommendation="BUY",
    )


policy = DecisionPolicy()

engine = DecisionEngine()

analysis = create_analysis(85)

valuation = create_value(20)

result = engine.evaluate(
    analysis,
    valuation,
    policy,
)

print(result)