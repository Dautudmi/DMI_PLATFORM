from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from apps.portfolio.models.holding_analysis import HoldingAnalysis
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.portfolio_recommendation import (
    PortfolioRecommendation,
)


@dataclass(slots=True)
class PortfolioReport:
    """
    Complete portfolio analysis report.

    This object is the primary output of PortfolioAnalyzer and serves as
    the data contract for all exporters (Excel, Telegram, Dashboard, API).
    """

    portfolio: Portfolio

    holding_analyses: list[HoldingAnalysis] = field(default_factory=list)

    recommendations: list[PortfolioRecommendation] = field(default_factory=list)

    summary: dict[str, Any] = field(default_factory=dict)

    generated_at: datetime = field(default_factory=datetime.now)