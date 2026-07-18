from apps.portfolio.report.portfolio_report import PortfolioReport
from dmi_core.portfolio import PortfolioEvaluation


class PortfolioReportBuilder:
    """
    Build presentation-ready report from PortfolioEvaluation.
    """

    def build(
        self,
        evaluation: PortfolioEvaluation,
    ) -> PortfolioReport:
        highlights: list[str] = []
        suggested_actions: list[str] = []

        for insight in evaluation.insights.insights:
            highlights.append(insight.message)

            if insight.suggested_action:
                suggested_actions.append(insight.suggested_action)

        return PortfolioReport(
            client_name=evaluation.portfolio.client_name,
            health_level=evaluation.health.level.value.upper(),
            health_score=evaluation.health.score,
            highlights=highlights,
            suggested_actions=suggested_actions,
            decision=None,
            confidence=None,
            decision_explanation=None,
        )