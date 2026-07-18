from apps.portfolio.models.holding_analysis import HoldingAnalysis
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.shared.pipeline.result import PipelineResult


class HoldingAnalysisFactory:
    """
    Build HoldingAnalysis from PipelineResult.
    """

    @staticmethod
    def from_pipeline(
        result: PipelineResult,
    ) -> HoldingAnalysis:

        context = result.context

        return HoldingAnalysis(
            symbol=context.holding.symbol,
            quantity=context.holding.quantity,
            average_cost=context.holding.average_cost,
            current_price=context.holding.current_price,
            position=context.position,
            dmi_report=context.dmi_report,
        )