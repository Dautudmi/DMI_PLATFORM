from dmi_core.metrics import FinancialMetrics
from dmi_core.models.analysis_result import AnalysisResult
from dmi_core.models.financial_analysis_result import FinancialAnalysisResult
from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.rules import LeverageRules, ProfitabilityRules
from dmi_core.scoring import ScoringEngine


class FinancialAnalysis:
    """
    DMI Financial Analysis Engine.

    This layer converts Financial Metrics into business conclusions.
    """

    def __init__(self, statement: FinancialStatement):
        self.statement = statement
        self.metrics = FinancialMetrics(statement)

    def profitability(self) -> AnalysisResult:
        """
        Analyze profitability using ProfitabilityRules.
        """

        roe = self.metrics.roe().value
        return ProfitabilityRules.evaluate(roe=roe)

    def leverage(self) -> AnalysisResult:
        """
        Analyze leverage using LeverageRules.
        """

        debt_to_equity = self.metrics.debt_to_equity().value
        return LeverageRules.evaluate(debt_to_equity=debt_to_equity)

    def analyze(self) -> FinancialAnalysisResult:
        """
        Run all financial analyses and return aggregate result.
        """

        profitability = self.profitability()
        leverage = self.leverage()

        results = [
            profitability,
            leverage,
        ]

        overall_score, overall_rating, recommendation = ScoringEngine.evaluate(
            results
        )

        return FinancialAnalysisResult(
            profitability=profitability,
            leverage=leverage,
            overall_score=overall_score,
            overall_rating=overall_rating,
            recommendation=recommendation,
        )

    def summary(self) -> list[AnalysisResult]:
        """
        Return all individual analysis results.
        """

        return [
            self.profitability(),
            self.leverage(),
        ]