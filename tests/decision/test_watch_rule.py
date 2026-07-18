from __future__ import annotations

from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.decision.rules.watch_rule import (
    WatchRule,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


def create_analysis(
    overall_score: int = 65,
) -> FinancialAnalysisResult:
    return FinancialAnalysisResult(
        overall_score=overall_score,
    )


def create_valuation(
    margin_of_safety: float | None = 0.0,
) -> ValuationResult:
    return ValuationResult(
        method="TEST",
        intrinsic_value=100.0,
        current_price=100.0,
        upside=0.0,
        downside=0.0,
        margin_of_safety=margin_of_safety,
        recommendation="WATCH",
    )


def test_watch_rule_returns_result() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(
            overall_score=65,
        ),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "WATCH"


def test_watch_rule_returns_three_stars() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.stars == 3


def test_watch_rule_score_at_threshold() -> None:
    policy = DecisionPolicy(
        min_score_watch=60,
    )

    result = WatchRule().evaluate(
        analysis=create_analysis(
            overall_score=60,
        ),
        valuation=create_valuation(),
        policy=policy,
    )

    assert result is not None
    assert result.recommendation == "WATCH"


def test_watch_rule_rejects_score_below_threshold() -> None:
    policy = DecisionPolicy(
        min_score_watch=60,
    )

    result = WatchRule().evaluate(
        analysis=create_analysis(
            overall_score=59,
        ),
        valuation=create_valuation(),
        policy=policy,
    )

    assert result is None


def test_watch_rule_uses_custom_policy_threshold() -> None:
    policy = DecisionPolicy(
        min_score_watch=75,
    )

    result = WatchRule().evaluate(
        analysis=create_analysis(
            overall_score=70,
        ),
        valuation=create_valuation(),
        policy=policy,
    )

    assert result is None


def test_watch_rule_does_not_require_positive_mos() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(
            overall_score=65,
        ),
        valuation=create_valuation(
            margin_of_safety=-50.0,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "WATCH"


def test_watch_rule_accepts_none_mos() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(
            overall_score=65,
        ),
        valuation=create_valuation(
            margin_of_safety=None,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "WATCH"


def test_watch_rule_returns_confidence() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert isinstance(result.confidence, int)
    assert 0 <= result.confidence <= 100


def test_watch_rule_summary() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert (
        result.summary
        == (
            "Company is acceptable but "
            "not yet attractive."
        )
    )


def test_watch_rule_reasons() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert result.reasons == [
        "Financial quality is average.",
    ]


def test_watch_rule_risks() -> None:
    result = WatchRule().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result is not None

    assert result.risks == [
        "Valuation is not attractive enough.",
    ]