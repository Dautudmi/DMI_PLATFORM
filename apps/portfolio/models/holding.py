from dataclasses import dataclass


@dataclass(slots=True)
class Holding:
    """
    A single stock holding in a portfolio.
    """

    symbol: str

    quantity: float

    average_cost: float

    current_price: float | None = None

    market_value: float = 0.0

    unrealized_pnl: float = 0.0

    unrealized_return: float = 0.0