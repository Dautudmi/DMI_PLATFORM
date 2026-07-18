from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24Strategy:
    symbol: str
    strategy: str
    raw: dict | None = None