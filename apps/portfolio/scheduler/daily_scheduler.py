from datetime import datetime, date
from typing import Callable, Any

from apps.portfolio.scheduler.daily_schedule import DailySchedule
from apps.portfolio.scheduler.daily_scheduler_result import DailySchedulerResult


class DailyScheduler:
    """
    Simple in-process daily scheduler.

    Responsibility:
    - kiểm tra đã đến giờ chạy chưa
    - đảm bảo mỗi ngày chỉ chạy một lần
    - gọi job được truyền vào

    Không chứa business logic portfolio.
    Không gửi Telegram.
    Không render.
    Không đọc file.
    Không phụ thuộc Windows Task Scheduler.
    """

    def __init__(
        self,
        schedule: DailySchedule,
        job: Callable[[], Any],
    ):
        if schedule is None:
            raise ValueError("schedule must not be None")

        if job is None:
            raise ValueError("job must not be None")

        self._schedule = schedule
        self._job = job
        self._last_run_date: date | None = None

    @property
    def schedule(self) -> DailySchedule:
        return self._schedule

    @property
    def last_run_date(self) -> date | None:
        return self._last_run_date

    def tick(self, now: datetime | None = None) -> DailySchedulerResult:
        checked_at = now or datetime.now()

        if not self._should_run(checked_at):
            return DailySchedulerResult(
                should_run=False,
                executed=False,
                checked_at=checked_at,
                data=None,
                error=None,
            )

        try:
            data = self._job()
            self._last_run_date = checked_at.date()

            return DailySchedulerResult(
                should_run=True,
                executed=True,
                checked_at=checked_at,
                data=data,
                error=None,
            )

        except Exception as exc:
            return DailySchedulerResult(
                should_run=True,
                executed=False,
                checked_at=checked_at,
                data=None,
                error=str(exc),
            )

    def _should_run(self, now: datetime) -> bool:
        if self._last_run_date == now.date():
            return False

        current_time = now.time().replace(second=0, microsecond=0)

        return current_time >= self._schedule.run_time