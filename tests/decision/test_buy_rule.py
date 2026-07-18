from __future__ import annotations

from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.decision.rules.buy_rule import (
    BuyRule,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


def create_analysis(
    overall_score: int = 75,
) -> FinancialAnalysisResult:
    return FinancialAnalysisResult(
        overall_score=overall_score,
    )


def create_valuation(
    margin_of_safety: float | None = 0.12,
) -> ValuationResult:
    return ValuationResult(
        method="TEST",
        intrinsic_value=100.0,
        current_price=88.0,
        upside=0.1364,
        downside=0.0,
        margin_of_safety=margin_of_safety,
        recommendation="BUY",
    )


def test_buy_rule_returns_result() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=75,
        ),
        valuation=create_valuation(
            margin_of_safety=0.12,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "BUY"


def test_buy_rule_returns_four_stars() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.stars == 4


def test_buy_rule_uses_policy_stars() -> None:
    policy = DecisionPolicy(
        buy_stars=3,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=policy,
    )

    assert result is not None
    assert result.stars == 3


def test_buy_rule_score_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_regular_buy=70,
        min_margin_of_safety_buy=0.10,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=70,
        ),
        valuation=create_valuation(
            margin_of_safety=0.12,
        ),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "BUY"


def test_buy_rule_mos_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_regular_buy=70,
        min_margin_of_safety_buy=0.10,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=75,
        ),
        valuation=create_valuation(
            margin_of_safety=0.10,
        ),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "BUY"


def test_buy_rule_both_values_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_regular_buy=70,
        min_margin_of_safety_buy=0.10,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=70,
        ),
        valuation=create_valuation(
            margin_of_safety=0.10,
        ),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "BUY"


def test_buy_rule_rejects_low_score() -> None:
    policy = DecisionPolicy(
        min_score_regular_buy=70,
        min_margin_of_safety_buy=0.10,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=69,
        ),
        valuation=create_valuation(
            margin_of_safety=0.20,
        ),
        policy=policy,
    )

    assert result is None


def test_buy_rule_rejects_low_mos() -> None:
    policy = DecisionPolicy(
        min_score_regular_buy=70,
        min_margin_of_safety_buy=0.10,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=80,
        ),
        valuation=create_valuation(
            margin_of_safety=0.0999,
        ),
        policy=policy,
    )

    assert result is None


def test_buy_rule_returns_confidence() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert isinstance(
        result.confidence,
        int,
    )
    assert 0 <= result.confidence <= 100


def test_buy_rule_summary() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert result.summary == (
        "Good financial quality with "
        "reasonable valuation."
    )


def test_buy_rule_reasons() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert result.reasons == [
        "Financial score is good.",
        "Valuation is acceptable.",
    ]


def test_buy_rule_has_no_risks() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.risks == []


def test_buy_rule_uses_custom_policy_thresholds() -> None:
    policy = DecisionPolicy(
        min_score_regular_buy=80,
        min_margin_of_safety_buy=0.20,
    )

    result = BuyRule().evaluate(
        analysis=create_analysis(
            overall_score=75,
        ),
        valuation=create_valuation(
            margin_of_safety=0.12,
        ),
        policy=policy,
    )

    assert result is None


def test_buy_rule_none_mos_returns_none() -> None:
    result = BuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(
            margin_of_safety=None,
        ),
        policy=DecisionPolicy(),
    )

    assert result is None