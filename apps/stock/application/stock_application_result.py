from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StockApplicationResult:
    success: bool
    total_rows: int = 0
    total_symbols: int = 0
    data: Any | None = None
    error: str | None = None