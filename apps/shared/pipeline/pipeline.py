from apps.shared.pipeline.context import PipelineContext
from apps.shared.pipeline.result import PipelineResult
from apps.shared.pipeline.stage import PipelineStage


class Pipeline:
    """
    Executes pipeline stages sequentially.
    """

    def __init__(self, stages: list[PipelineStage]) -> None:
        self._stages = stages

    def execute(self, context: PipelineContext) -> PipelineResult:
        if not isinstance(context, PipelineContext):
            raise TypeError("Pipeline expects a PipelineContext instance")

        current_context = context

        for stage in self._stages:
            current_context = stage.run(current_context)

        return PipelineResult(context=current_context)