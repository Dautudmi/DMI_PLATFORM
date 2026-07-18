from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClientBatchItemResult:
    client_id: str
    success: bool
    data: Any | None = None
    error: str | None = None


@dataclass(frozen=True)
class ClientBatchResult:
    total_clients: int
    success_count: int
    failed_count: int
    results: list[ClientBatchItemResult] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.failed_count == 0

    @property
    def has_failed(self) -> bool:
        return self.failed_count > 0