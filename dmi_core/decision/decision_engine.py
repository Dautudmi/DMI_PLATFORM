from __future__ import annotations

from typing import TypeAlias

from dmi_core.models.financial_analysis_result import (
    FinancialAnalysisResult,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)

from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.decision.decision_result import (
    DecisionResult,
)
from dmi_core.decision.decision_rule_registry import (
    DecisionRuleRegistry,
)


DecisionValuationType: TypeAlias = (
    ValuationResult
    | WeightedFairValueResult
)


class DecisionEngine:
    """
    Evaluate investment decision using registered decision rules.

    DecisionEngine supports:
    - ValuationResult
    - WeightedFairValueResult

    WeightedFairValueResult is the preferred production input
    when multiple valuation methods are available.

    ValuationResult remains supported for backward compatibility.
    """

    def __init__(
        self,
        registry: DecisionRuleRegistry | None = None,
    ) -> None:
        if registry is None:
            registry = DecisionRuleRegistry.default()

        self._registry = registry

    @property
    def registry(
        self,
    ) -> DecisionRuleRegistry:
        return self._registry

    def evaluate(
        self,
        analysis: FinancialAnalysisResult,
        valuation: DecisionValuationType,
        policy: DecisionPolicy,
    ) -> DecisionResult:
        """
        Evaluate one final investment decision.

        The valuation argument can be:
        - a single-method ValuationResult
        - an aggregated WeightedFairValueResult
        """

        self._validate_analysis(
            analysis
        )

        self._validate_valuation(
            valuation
        )

        self._validate_policy(
            policy
        )

        for rule in self._registry.rules():
            result = rule.evaluate(
                analysis=analysis,
                valuation=valuation,
                policy=policy,
            )

            if result is not None:
                return result

        raise RuntimeError(
            "No decision rule produced a result"
        )

    def _validate_analysis(
        self,
        analysis: FinancialAnalysisResult,
    ) -> None:
        if analysis is None:
            raise ValueError(
                "analysis must not be None"
            )

        if not isinstance(
            analysis,
            FinancialAnalysisResult,
        ):
            raise TypeError(
                "analysis must be a "
                "FinancialAnalysisResult"
            )

    def _validate_valuation(
        self,
        valuation: DecisionValuationType,
    ) -> None:
        if valuation is None:
            raise ValueError(
                "valuation must not be None"
            )

        if not isinstance(
            valuation,
            (
                ValuationResult,
                WeightedFairValueResult,
            ),
        ):
            raise TypeError(
                "valuation must be a ValuationResult "
                "or WeightedFairValueResult"
            )

    def _validate_policy(
        self,
        policy: DecisionPolicy,
    ) -> None:
        if policy is None:
            raise ValueError(
                "policy must not be None"
            )

        if not isinstance(
            policy,
            DecisionPolicy,
        ):
            raise TypeError(
                "policy must be a DecisionPolicy"
            )