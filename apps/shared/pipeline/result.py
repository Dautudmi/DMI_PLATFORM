from dataclasses import dataclass

from apps.shared.pipeline.context import PipelineContext


@dataclass(slots=True)
class PipelineResult:
    """
    Result returned after pipeline execution.
    """

    context: PipelineContext

    @property
    def success(self) -> bool:
        return len(self.context.errors) == 0