from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PEV24IntegrationResult:
    success: bool
    total_clients: int = 0
    total_holdings: int = 0
    total_buy_candidates: int = 0
    total_strategies: int = 0
    data: Any | None = None
    error: str | None = None