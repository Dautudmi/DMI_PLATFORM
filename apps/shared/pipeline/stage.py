from abc import ABC, abstractmethod

from apps.shared.pipeline.context import PipelineContext


class PipelineStage(ABC):
    """
    Base class for a pipeline stage.
    """

    @abstractmethod
    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError