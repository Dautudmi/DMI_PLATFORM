from __future__ import annotations

import pytest

from dmi_core.decision import (
    DecisionEngine,
    DecisionPolicy,
)
from dmi_core.decision.decision_rule_registry import (
    DecisionRuleRegistry,
)
from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


def create_analysis(
    overall_score: int = 90,
) -> FinancialAnalysisResult:
    return FinancialAnalysisResult(
        overall_score=overall_score,
    )


def create_valuation(
    margin_of_safety: float = 0.20,
) -> ValuationResult:
    return ValuationResult(
        method="DCF",
        intrinsic_value=100.0,
        current_price=80.0,
        upside=0.25,
        downside=0.0,
        margin_of_safety=margin_of_safety,
        recommendation="BUY",
    )


def create_weighted_valuation(
    margin_of_safety: float = 0.20,
    recommendation: str = "BUY",
) -> WeightedFairValueResult:
    return WeightedFairValueResult(
        method="WEIGHTED",
        intrinsic_value=100.0,
        current_price=80.0,
        upside=0.25,
        downside=0.0,
        margin_of_safety=margin_of_safety,
        recommendation=recommendation,
        components=(),
        normalized_weights={},
        description=(
            "Weighted fair value used by "
            "DecisionEngine test."
        ),
    )


def test_decision_engine_can_be_created() -> None:
    engine = DecisionEngine()

    assert engine is not None


def test_decision_engine_returns_decision() -> None:
    result = DecisionEngine().evaluate(
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


def test_decision_engine_accepts_weighted_fair_value() -> None:
    result = DecisionEngine().evaluate(
        analysis=create_analysis(
            overall_score=90,
        ),
        valuation=create_weighted_valuation(
            margin_of_safety=0.20,
        ),
        policy=DecisionPolicy(),
    )

    assert result is not None
    assert result.recommendation == "STRONG BUY"


def test_decision_engine_returns_buy() -> None:
    result = DecisionEngine().evaluate(
        analysis=create_analysis(
            overall_score=75,
        ),
        valuation=create_valuation(
            margin_of_safety=0.12,
        ),
        policy=DecisionPolicy(),
    )

    assert result.recommendation == "BUY"


def test_decision_engine_returns_watch() -> None:
    result = DecisionEngine().evaluate(
        analysis=create_analysis(
            overall_score=65,
        ),
        valuation=create_valuation(
            margin_of_safety=0.05,
        ),
        policy=DecisionPolicy(),
    )

    assert result.recommendation == "WATCH"


def test_decision_engine_returns_sell() -> None:
    result = DecisionEngine().evaluate(
        analysis=create_analysis(
            overall_score=50,
        ),
        valuation=create_valuation(
            margin_of_safety=-0.10,
        ),
        policy=DecisionPolicy(),
    )

    assert result.recommendation == "SELL"


def test_decision_engine_preserves_single_valuation_support() -> None:
    result = DecisionEngine().evaluate(
        analysis=create_analysis(),
        valuation=create_valuation(),
        policy=DecisionPolicy(),
    )

    assert result.recommendation == "STRONG BUY"


def test_decision_engine_rejects_none_analysis() -> None:
    with pytest.raises(
        ValueError,
        match="analysis must not be None",
    ):
        DecisionEngine().evaluate(
            analysis=None,
            valuation=create_valuation(),
            policy=DecisionPolicy(),
        )


def test_decision_engine_rejects_invalid_analysis() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "analysis must be a "
            "FinancialAnalysisResult"
        ),
    ):
        DecisionEngine().evaluate(
            analysis=object(),
            valuation=create_valuation(),
            policy=DecisionPolicy(),
        )


def test_decision_engine_rejects_none_valuation() -> None:
    with pytest.raises(
        ValueError,
        match="valuation must not be None",
    ):
        DecisionEngine().evaluate(
            analysis=create_analysis(),
            valuation=None,
            policy=DecisionPolicy(),
        )


def test_decision_engine_rejects_invalid_valuation() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "valuation must be a ValuationResult "
            "or WeightedFairValueResult"
        ),
    ):
        DecisionEngine().evaluate(
            analysis=create_analysis(),
            valuation=object(),
            policy=DecisionPolicy(),
        )


def test_decision_engine_rejects_none_policy() -> None:
    with pytest.raises(
        ValueError,
        match="policy must not be None",
    ):
        DecisionEngine().evaluate(
            analysis=create_analysis(),
            valuation=create_valuation(),
            policy=None,
        )


def test_decision_engine_rejects_invalid_policy() -> None:
    with pytest.raises(
        TypeError,
        match="policy must be a DecisionPolicy",
    ):
        DecisionEngine().evaluate(
            analysis=create_analysis(),
            valuation=create_valuation(),
            policy=object(),
        )


def test_decision_engine_exposes_registry() -> None:
    registry = DecisionRuleRegistry.default()

    engine = DecisionEngine(
        registry=registry,
    )

    assert engine.registry is registry