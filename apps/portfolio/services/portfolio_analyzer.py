from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.report import PortfolioReport
from apps.portfolio.services.holding_analyzer import HoldingAnalyzer


class PortfolioAnalyzer:
    """
    Analyze an investment portfolio.

    Responsibilities
    ----------------
    - Validate Portfolio
    - Analyze each Holding
    - Build PortfolioReport

    Future versions will integrate:
        - DMI Engine
        - Decision Engine
        - Allocation Analyzer
        - Risk Analyzer
    """

    def __init__(self) -> None:
        self._holding_analyzer = HoldingAnalyzer()

    def analyze(self, portfolio: Portfolio) -> PortfolioReport:
        if not isinstance(portfolio, Portfolio):
            raise TypeError(
                "PortfolioAnalyzer expects a Portfolio instance"
            )

        analyses = []

        for holding in portfolio.holdings:
            analyses.append(
                self._holding_analyzer.analyze(holding)
            )

        return PortfolioReport(
            portfolio=portfolio,
            holding_analyses=analyses,
            recommendations=[],
            summary={},
        )