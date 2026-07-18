from dataclasses import dataclass


@dataclass(slots=True)
class PositionAnalysis:
    """
    Position-level analysis for a holding.

    This contains derived values calculated from quantity,
    average_cost, and current_price.
    """

    market_value: float
    cost_value: float
    unrealized_pnl: float
    unrealized_return: float