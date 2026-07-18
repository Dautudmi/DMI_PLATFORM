from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class DailySchedule:
    hour: int
    minute: int = 0

    def __post_init__(self):
        if self.hour < 0 or self.hour > 23:
            raise ValueError("hour must be between 0 and 23")

        if self.minute < 0 or self.minute > 59:
            raise ValueError("minute must be between 0 and 59")

    @property
    def run_time(self) -> time:
        return time(hour=self.hour, minute=self.minute)