from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioMetrics:
    """
    Objective portfolio metrics.

    Metrics describe facts.
    They do not evaluate health.
    """

    total_value: float
    cash_value: float
    cash_weight: float
    number_of_holdings: int
    largest_position_weight: float
    concentration_ratio: float