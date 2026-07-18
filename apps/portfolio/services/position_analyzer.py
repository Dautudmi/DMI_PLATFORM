from apps.portfolio.models.holding import Holding
from apps.portfolio.models.position_analysis import PositionAnalysis


class PositionAnalyzer:
    """
    Analyze position-level metrics for a holding.

    This service only calculates values derived from:
    - quantity
    - average_cost
    - current_price

    It must not depend on CSV, API, Database, DMI Engine, or Telegram.
    """

    def analyze(self, holding: Holding) -> PositionAnalysis:
        if not isinstance(holding, Holding):
            raise TypeError("PositionAnalyzer expects a Holding instance")

        cost_value = holding.quantity * holding.average_cost

        if holding.current_price is None:
            return PositionAnalysis(
                market_value=0.0,
                cost_value=cost_value,
                unrealized_pnl=0.0,
                unrealized_return=0.0,
            )

        market_value = holding.quantity * holding.current_price
        unrealized_pnl = market_value - cost_value
        unrealized_return = (
            unrealized_pnl / cost_value
            if cost_value != 0
            else 0.0
        )

        return PositionAnalysis(
            market_value=market_value,
            cost_value=cost_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_return=unrealized_return,
        )