from apps.portfolio.factories import HoldingAnalysisFactory
from apps.portfolio.models.holding import Holding
from apps.portfolio.models.holding_analysis import HoldingAnalysis
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.pipeline.holding_pipeline import HoldingPipeline


class HoldingAnalyzer:
    """
    Application service responsible for holding analysis.

    Business workflow is delegated to HoldingPipeline.
    """

    def __init__(
        self,
        pipeline: HoldingPipeline | None = None,
    ) -> None:
        self._pipeline = pipeline or HoldingPipeline()

    def analyze(
        self,
        holding: Holding,
    ) -> HoldingAnalysis:
        if not isinstance(holding, Holding):
            raise TypeError("HoldingAnalyzer expects a Holding instance")

        context = HoldingPipelineContext(
            holding=holding,
        )

        result = self._pipeline.execute(context)

        return HoldingAnalysisFactory.from_pipeline(result)