from dataclasses import dataclass

from infrastructure.pe_v24.pe_v24_client_config import PEV24ClientConfig
from infrastructure.pe_v24.pe_v24_client_position import (
    PEV24ClientPosition,
)


@dataclass(frozen=True)
class PEV24ClientDataResult:
    success: bool
    client_id: str
    client_config: PEV24ClientConfig | None = None
    positions: list[PEV24ClientPosition] | None = None
    error: str | None = None

    @property
    def total_positions(self) -> int:
        if self.positions is None:
            return 0

        return len(self.positions)