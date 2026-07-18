from dataclasses import dataclass, field
from datetime import datetime

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.portfolio_insight import PortfolioInsight
from apps.portfolio.models.portfolio_recommendation import PortfolioRecommendation


@dataclass(slots=True)
class PortfolioIntelligenceReport:
    """
    High-level intelligence report for a client portfolio.
    """

    portfolio: Portfolio
    insights: list[PortfolioInsight] = field(default_factory=list)
    recommendations: list[PortfolioRecommendation] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)