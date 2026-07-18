from __future__ import annotations

from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.decision.rules.strong_buy_rule import (
    StrongBuyRule,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


def create_analysis(
    overall_score: int = 90,
) -> FinancialAnalysisResult:
    return FinancialAnalysisResult(
        overall_score=overall_score,
    )


def create_valuation(
    margin_of_safety: float | None = 0.20,
) -> ValuationResult:
    return ValuationResult(
        method="TEST",
        intrinsic_value=100.0,
        current_price=80.0,
        upside=0.25,
        downside=0.0,
        margin_of_safety=margin_of_safety,
        recommendation="BUY",
    )


def test_strong_buy_rule_returns_result() -> None:
    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=90,
        ),
        valuation=create_valuation(
            margin_of_safety=0.20,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "STRONG BUY"


def test_strong_buy_rule_returns_five_stars() -> None:
    result = StrongBuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.stars == 5


def test_strong_buy_rule_uses_policy_stars() -> None:
    policy = DecisionPolicy(
        strong_buy_stars=4,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=policy,
    )

    assert result is not None
    assert result.stars == 4


def test_strong_buy_rule_returns_confidence() -> None:
    result = StrongBuyRule().evaluate(
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


def test_strong_buy_rule_score_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_buy=80,
        min_margin_of_safety=0.15,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=80,
        ),
        valuation=create_valuation(
            margin_of_safety=0.20,
        ),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "STRONG BUY"


def test_strong_buy_rule_mos_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_buy=80,
        min_margin_of_safety=0.15,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=90,
        ),
        valuation=create_valuation(
            margin_of_safety=0.15,
        ),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "STRONG BUY"


def test_strong_buy_rule_both_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_buy=80,
        min_margin_of_safety=0.15,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=80,
        ),
        valuation=create_valuation(
            margin_of_safety=0.15,
        ),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "STRONG BUY"


def test_strong_buy_rule_rejects_low_score() -> None:
    policy = DecisionPolicy(
        min_score_buy=80,
        min_margin_of_safety=0.15,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=79,
        ),
        valuation=create_valuation(
            margin_of_safety=0.20,
        ),
        policy=policy,
    )

    assert result is None


def test_strong_buy_rule_rejects_low_mos() -> None:
    policy = DecisionPolicy(
        min_score_buy=80,
        min_margin_of_safety=0.15,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=90,
        ),
        valuation=create_valuation(
            margin_of_safety=0.1499,
        ),
        policy=policy,
    )

    assert result is None


def test_strong_buy_rule_none_mos_returns_none() -> None:
    result = StrongBuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(
            margin_of_safety=None,
        ),
        policy=DecisionPolicy(),
    )

    assert result is None


def test_strong_buy_rule_summary() -> None:
    result = StrongBuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert result.summary == (
        "Excellent financial quality "
        "with attractive valuation."
    )


def test_strong_buy_rule_reasons() -> None:
    result = StrongBuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert result.reasons == [
        "Financial score is excellent.",
        "Margin of Safety is attractive.",
    ]


def test_strong_buy_rule_has_no_risks() -> None:
    result = StrongBuyRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.risks == []


def test_strong_buy_rule_uses_custom_policy() -> None:
    policy = DecisionPolicy(
        min_score_buy=95,
        min_margin_of_safety=0.25,
    )

    result = StrongBuyRule().evaluate(
        analysis=create_analysis(
            overall_score=90,
        ),
        valuation=create_valuation(
            margin_of_safety=0.20,
        ),
        policy=policy,
    )

    assert result is None