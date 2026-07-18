from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.services.dmi_service import DMIService
from apps.shared.pipeline.context import PipelineContext
from apps.shared.pipeline.stage import PipelineStage


class AnalysisStage(PipelineStage):
    """
    Pipeline stage that runs DMI analysis from financial statement.
    """

    def __init__(
        self,
        dmi_service: DMIService | None = None,
    ) -> None:
        self._dmi_service = dmi_service or DMIService()

    def run(self, context: PipelineContext) -> PipelineContext:
        if not isinstance(context, HoldingPipelineContext):
            raise TypeError(
                "AnalysisStage expects a HoldingPipelineContext instance"
            )

        if context.holding is None:
            context.errors.append("Missing holding")
            return context

        if context.financial_statement is None:
            context.errors.append("Missing financial statement")
            return context

        context.dmi_report = self._dmi_service.analyze(
            statement=context.financial_statement,
            current_price=context.holding.current_price,
        )

        return context