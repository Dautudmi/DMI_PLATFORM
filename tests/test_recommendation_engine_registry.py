from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio

from dmi_core.portfolio import PortfolioEvaluator
from dmi_core.recommendation import Recommendation
from dmi_core.recommendation.recommendation_engine import RecommendationEngine
from dmi_core.recommendation.recommendation_rule_registry import (
    RecommendationRuleRegistry,
)
from dmi_core.recommendation.rules import RecommendationRule


class DummyRule(RecommendationRule):

    def evaluate(self, evaluation):
        return Recommendation(
            title="Dummy",
            action="Dummy Action",
            priority=1,
        )


def test_engine_runs_registered_rules():

    portfolio = Portfolio(
        client_name="Demo",
        cash=1_000_000,
        holdings=[
            Holding(
                symbol="FPT",
                quantity=100,
                average_cost=80_000,
                current_price=100_000,
            )
        ],
    )

    evaluation = PortfolioEvaluator().evaluate(portfolio)

    registry = RecommendationRuleRegistry()
    registry.register(DummyRule())

    engine = RecommendationEngine(registry)

    result = engine.generate(evaluation)

    assert len(result) == 1