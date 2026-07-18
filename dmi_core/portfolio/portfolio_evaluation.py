from dataclasses import dataclass

from apps.portfolio.models.portfolio import Portfolio

from dmi_core.health import PortfolioHealth
from dmi_core.insights import InsightCollection
from dmi_core.metrics import PortfolioMetrics


@dataclass(slots=True)
class PortfolioEvaluation:
    """
    Aggregate root representing the complete portfolio evaluation.
    """

    portfolio: Portfolio
    metrics: PortfolioMetrics
    health: PortfolioHealth
    insights: InsightCollection
    summary: str | None = None