from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioRecommendation:
    """
    Recommendation for one holding.
    """

    symbol: str

    action: str

    confidence: float

    reason: str