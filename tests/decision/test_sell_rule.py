from __future__ import annotations

from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.decision.rules.sell_rule import (
    SellRule,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


def create_analysis(
    overall_score: int = 40,
) -> FinancialAnalysisResult:
    return FinancialAnalysisResult(
        overall_score=overall_score,
    )


def create_valuation(
    margin_of_safety: float | None = -20.0,
) -> ValuationResult:
    return ValuationResult(
        method="TEST",
        intrinsic_value=80.0,
        current_price=100.0,
        upside=-20.0,
        downside=20.0,
        margin_of_safety=margin_of_safety,
        recommendation="AVOID",
    )


def test_sell_rule_returns_result() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "SELL"


def test_sell_rule_returns_two_stars() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result.stars == 2


def test_sell_rule_returns_confidence() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert isinstance(
        result.confidence,
        int,
    )

    assert 0 <= result.confidence <= 100


def test_sell_rule_summary() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert (
        result.summary
        == (
            "Financial quality is below "
            "the investment threshold."
        )
    )


def test_sell_rule_has_no_positive_reasons() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result.reasons == []


def test_sell_rule_contains_financial_risk() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result.risks == [
        "Financial score is low.",
    ]


def test_sell_rule_always_returns_result() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(
            overall_score=100,
        ),
        valuation=create_valuation(
            margin_of_safety=100.0,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "SELL"


def test_sell_rule_accepts_none_mos() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(
            margin_of_safety=None,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "SELL"


def test_sell_rule_ignores_policy_thresholds() -> None:
    policy = DecisionPolicy(
        min_score_buy=100,
        min_score_watch=100,
        min_margin_of_safety=100.0,
    )

    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "SELL"


def test_sell_rule_result_can_explain_itself() -> None:
    result = SellRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    explanation = result.explain()

    assert "Decision: SELL" in explanation
    assert "Financial score is low." in explanation