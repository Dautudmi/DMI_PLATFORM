from dmi_core.portfolio import PortfolioEvaluation
from dmi_core.recommendation.recommendation_collection import RecommendationCollection
from dmi_core.recommendation.recommendation_rule_registry import (
    RecommendationRuleRegistry,
)


class RecommendationEngine:
    """
    Execute registered recommendation rules.
    """

    def __init__(
        self,
        registry: RecommendationRuleRegistry,
    ) -> None:
        self._registry = registry

    def generate(
        self,
        evaluation: PortfolioEvaluation,
    ) -> RecommendationCollection:

        collection = RecommendationCollection()

        for rule in self._registry.rules():

            recommendation = rule.evaluate(evaluation)

            if recommendation is not None:
                collection.add(recommendation)

        return collection