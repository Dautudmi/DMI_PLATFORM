from dmi_core.metrics import PortfolioMetrics

from apps.portfolio.models.portfolio import Portfolio


class PortfolioMetricsCalculator:
    """
    Calculate objective metrics from a portfolio.

    This class contains no business policy.
    """

    def calculate(
        self,
        portfolio: Portfolio,
    ) -> PortfolioMetrics:

        total_position_value = 0.0
        largest_position = 0.0

        for holding in portfolio.holdings:

            if holding.current_price is None:
                continue

            value = holding.quantity * holding.current_price

            total_position_value += value

            largest_position = max(
                largest_position,
                value,
            )

        total_value = total_position_value + portfolio.cash

        if total_value == 0:
            return PortfolioMetrics(
                total_value=0.0,
                cash_value=0.0,
                cash_weight=0.0,
                number_of_holdings=0,
                largest_position_weight=0.0,
                concentration_ratio=0.0,
            )

        cash_weight = portfolio.cash / total_value

        largest_weight = (
            largest_position / total_value
            if total_value > 0
            else 0.0
        )

        return PortfolioMetrics(
            total_value=total_value,
            cash_value=portfolio.cash,
            cash_weight=cash_weight,
            number_of_holdings=len(portfolio.holdings),
            largest_position_weight=largest_weight,
            concentration_ratio=largest_weight,
        )