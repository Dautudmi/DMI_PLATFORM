from dmi_core.recommendation.rules import RecommendationRule


class RecommendationRuleRegistry:
    """
    Registry of all recommendation rules.
    """

    def __init__(self) -> None:
        self._rules: list[RecommendationRule] = []

    def register(
        self,
        rule: RecommendationRule,
    ) -> None:
        self._rules.append(rule)

    def rules(self) -> list[RecommendationRule]:
        return list(self._rules)