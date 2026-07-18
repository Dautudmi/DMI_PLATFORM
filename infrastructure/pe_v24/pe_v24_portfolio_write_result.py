from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PEV24PortfolioWriteResult:
    success: bool
    client_id: str
    file_path: str
    total_positions: int = 0
    backup_path: str | None = None
    error: str | None = None