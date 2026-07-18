from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24BuyCandidate:
    symbol: str
    strategy: str | None = None
    score: float | None = None
    raw: dict | None = None