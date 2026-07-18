from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24Holding:
    client_id: str
    symbol: str
    quantity: float | None = None
    cost_price: float | None = None
    raw: dict | None = None