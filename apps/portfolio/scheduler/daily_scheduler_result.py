from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DailySchedulerResult:
    should_run: bool
    executed: bool
    checked_at: datetime
    data: Any | None = None
    error: str | None = None