from dataclasses import dataclass, field

from .portfolio_recommendation import PortfolioRecommendation


@dataclass(slots=True)
class PortfolioReport:
    """
    Final portfolio analysis report.
    """

    portfolio_score: float

    overall_risk: str

    recommendations: list[PortfolioRecommendation] = field(
        default_factory=list
    )

    summary: str = ""