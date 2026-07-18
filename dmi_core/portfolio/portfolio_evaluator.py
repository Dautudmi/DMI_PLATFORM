from apps.portfolio.models.portfolio import Portfolio

from dmi_core.portfolio.portfolio_evaluation import PortfolioEvaluation
from dmi_core.portfolio.portfolio_health_evaluator import (
    PortfolioHealthEvaluator,
)
from dmi_core.portfolio.portfolio_insight_generator import (
    PortfolioInsightGenerator,
)
from dmi_core.portfolio.portfolio_metrics_calculator import (
    PortfolioMetricsCalculator,
)


class PortfolioEvaluator:
    """
    High-level facade for portfolio evaluation.

    This class orchestrates the complete portfolio evaluation pipeline.
    """

    def __init__(self) -> None:
        self._metrics = PortfolioMetricsCalculator()
        self._health = PortfolioHealthEvaluator()
        self._insights = PortfolioInsightGenerator()

    def evaluate(
        self,
        portfolio: Portfolio,
    ) -> PortfolioEvaluation:

        metrics = self._metrics.calculate(portfolio)

        health = self._health.evaluate(metrics)

        insights = self._insights.generate(
            metrics,
            health,
        )

        summary = (
            f"Portfolio Health: "
            f"{health.level.value.upper()} "
            f"({health.score}/100)"
        )

        return PortfolioEvaluation(
            portfolio=portfolio,
            metrics=metrics,
            health=health,
            insights=insights,
            summary=summary,
        )