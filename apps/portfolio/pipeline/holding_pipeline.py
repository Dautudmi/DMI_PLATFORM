from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.pipeline.stages.analysis_stage import AnalysisStage
from apps.portfolio.pipeline.stages.financial_stage import FinancialStage
from apps.portfolio.pipeline.stages.position_stage import PositionStage
from apps.portfolio.providers.financial_data_provider import FinancialDataProvider
from apps.portfolio.providers.null_financial_data_provider import NullFinancialDataProvider
from apps.portfolio.services.dmi_service import DMIService
from apps.portfolio.services.position_analyzer import PositionAnalyzer
from apps.shared.pipeline import Pipeline
from apps.shared.pipeline import PipelineResult


class HoldingPipeline:
    """
    Holding-level intelligence pipeline.

    Stages:
    - PositionStage
    - FinancialStage
    - AnalysisStage
    """

    def __init__(
        self,
        position_analyzer: PositionAnalyzer | None = None,
        financial_provider: FinancialDataProvider | None = None,
        dmi_service: DMIService | None = None,
    ) -> None:
        self._position_stage = PositionStage(
            position_analyzer=position_analyzer,
        )

        self._financial_stage = FinancialStage(
            financial_provider=(
                financial_provider
                if financial_provider is not None
                else NullFinancialDataProvider()
            ),
        )

        self._analysis_stage = AnalysisStage(
            dmi_service=dmi_service,
        )

        self._pipeline = Pipeline(
            stages=[
                self._position_stage,
                self._financial_stage,
                self._analysis_stage,
            ]
        )

    def execute(
        self,
        context: HoldingPipelineContext,
    ) -> PipelineResult:
        return self._pipeline.execute(context)