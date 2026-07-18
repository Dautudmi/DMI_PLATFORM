from dataclasses import dataclass

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.position_analysis import PositionAnalysis
from apps.shared.pipeline.context import PipelineContext


@dataclass(slots=True)
class HoldingPipelineContext(PipelineContext):
    """
    Pipeline context for holding-level intelligence analysis.
    """

    holding: Holding | None = None
    position: PositionAnalysis | None = None
    financial_statement: object | None = None
    dmi_report: object | None = None