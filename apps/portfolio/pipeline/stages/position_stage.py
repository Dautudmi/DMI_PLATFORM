from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.services.position_analyzer import PositionAnalyzer
from apps.shared.pipeline.context import PipelineContext
from apps.shared.pipeline.stage import PipelineStage


class PositionStage(PipelineStage):
    """
    Pipeline stage that calculates position analysis for a holding.
    """

    def __init__(
        self,
        position_analyzer: PositionAnalyzer | None = None,
    ) -> None:
        self._position_analyzer = (
            position_analyzer
            if position_analyzer is not None
            else PositionAnalyzer()
        )

    def run(self, context: PipelineContext) -> PipelineContext:
        if not isinstance(context, HoldingPipelineContext):
            raise TypeError(
                "PositionStage expects a HoldingPipelineContext instance"
            )

        if context.holding is None:
            context.errors.append("Missing holding")
            return context

        context.position = self._position_analyzer.analyze(
            context.holding
        )

        return context