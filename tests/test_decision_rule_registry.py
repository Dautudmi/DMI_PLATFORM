from dmi_core.decision.decision_rule_registry import (
    DecisionRuleRegistry,
)

from dmi_core.decision.rules import (
    StrongBuyRule,
    BuyRule,
    WatchRule,
    SellRule,
)


def test_default_registry_contains_four_rules():

    registry = DecisionRuleRegistry.default()

    rules = registry.rules()

    assert len(rules) == 4


def test_default_registry_rule_order():

    registry = DecisionRuleRegistry.default()

    rules = registry.rules()

    assert isinstance(rules[0], StrongBuyRule)
    assert isinstance(rules[1], BuyRule)
    assert isinstance(rules[2], WatchRule)
    assert isinstance(rules[3], SellRule)


def test_registry_returns_copy():

    registry = DecisionRuleRegistry.default()

    rules = registry.rules()

    rules.clear()

    assert len(registry.rules()) == 4