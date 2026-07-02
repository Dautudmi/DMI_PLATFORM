from dataclasses import dataclass
from typing import Optional

from dmi_core.models.analysis_result import AnalysisResult


@dataclass(slots=True)
class FinancialAnalysisResult:
    """
    Aggregate result of all financial analyses.
    """

    profitability: Optional[AnalysisResult] = None
    leverage: Optional[AnalysisResult] = None
    liquidity: Optional[AnalysisResult] = None
    efficiency: Optional[AnalysisResult] = None
    growth: Optional[AnalysisResult] = None

    overall_score: float = 0.0
    overall_rating: str = "Unknown"
    recommendation: str = "N/A"

    source: str = "DMI"
    schema_version: str = "2.2"