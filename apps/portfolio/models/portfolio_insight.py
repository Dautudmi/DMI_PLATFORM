from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioInsight:
    """
    Business insight generated from portfolio analysis.
    """

    category: str
    title: str
    message: str
    severity: str = "info"