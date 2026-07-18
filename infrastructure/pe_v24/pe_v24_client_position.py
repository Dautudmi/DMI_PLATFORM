from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24ClientPosition:
    """
    Một vị thế cổ phiếu trong danh mục khách hàng PE_V2.4.

    Format chuẩn mới:

    Ticker,Quantity,Cost
    NAB,1000,12.300
    """

    ticker: str
    cost: float
    quantity: float = 0.0
    raw: dict | None = None

    @property
    def symbol(self) -> str:
        """
        Alias tương thích với DMI Domain.
        """
        return self.ticker

    @property
    def average_cost(self) -> float:
        """
        Alias tương thích với Holding.average_cost.
        """
        return self.cost