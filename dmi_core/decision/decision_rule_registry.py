from dmi_core.decision.rules import (
    BuyRule,
    DecisionRule,
    SellRule,
    StrongBuyRule,
    WatchRule,
)


class DecisionRuleRegistry:
    """
    Registry for decision rules.

    Rules are evaluated in registration order.
    """

    def __init__(self) -> None:
        self._rules: list[DecisionRule] = []

    def register(
        self,
        rule: DecisionRule,
    ) -> None:
        self._rules.append(rule)

    def rules(self) -> list[DecisionRule]:
        return list(self._rules)

    @staticmethod
    def default() -> "DecisionRuleRegistry":
        registry = DecisionRuleRegistry()

        registry.register(StrongBuyRule())
        registry.register(BuyRule())
        registry.register(WatchRule())
        registry.register(SellRule())

        return registry