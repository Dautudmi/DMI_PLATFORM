from dataclasses import dataclass

from apps.portfolio.models.position_analysis import PositionAnalysis


@dataclass(slots=True)
class HoldingAnalysis:
    """
    Full analysis result for a single holding.
    """

    symbol: str
    quantity: float
    average_cost: float
    current_price: float | None
    position: PositionAnalysis
    dmi_report: object | None = None