from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioApplicationResult:
    success: bool
    total_clients: int
    success_count: int
    failed_count: int
    data: Any | None = None
    error: str | None = None

    @property
    def has_failed(self) -> bool:
        return self.failed_count > 0