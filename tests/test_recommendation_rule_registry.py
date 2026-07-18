from dmi_core.recommendation.recommendation_rule_registry import (
    RecommendationRuleRegistry,
)
from dmi_core.recommendation.rules import RecommendationRule


class DummyRule(RecommendationRule):
    def evaluate(self, evaluation):
        return None


def test_registry_registers_rule():

    registry = RecommendationRuleRegistry()

    registry.register(DummyRule())

    assert len(registry.rules()) == 1