from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.report import PortfolioReport, PortfolioReportBuilder
from dmi_core.portfolio import PortfolioEvaluator


class DailyPortfolioReportUseCase:
    def __init__(self) -> None:
        self._evaluator = PortfolioEvaluator()
        self._builder = PortfolioReportBuilder()

    def execute(self, portfolio: Portfolio) -> PortfolioReport:
        evaluation = self._evaluator.evaluate(portfolio)
        return self._builder.build(evaluation)