from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24StockRow:
    symbol: str
    date: str | None = None
    close: float | None = None
    volume: float | None = None
    raw: dict | None = None