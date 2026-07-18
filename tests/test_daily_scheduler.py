from datetime import datetime

from apps.portfolio.scheduler.daily_schedule import DailySchedule
from apps.portfolio.scheduler.daily_scheduler import DailyScheduler


def test_daily_schedule_rejects_invalid_hour():
    try:
        DailySchedule(hour=24, minute=0)
    except ValueError as exc:
        assert str(exc) == "hour must be between 0 and 23"
    else:
        assert False


def test_daily_schedule_rejects_invalid_minute():
    try:
        DailySchedule(hour=19, minute=60)
    except ValueError as exc:
        assert str(exc) == "minute must be between 0 and 59"
    else:
        assert False


def test_daily_scheduler_rejects_none_schedule():
    try:
        DailyScheduler(schedule=None, job=lambda: "ok")
    except ValueError as exc:
        assert str(exc) == "schedule must not be None"
    else:
        assert False


def test_daily_scheduler_rejects_none_job():
    try:
        DailyScheduler(schedule=DailySchedule(hour=19), job=None)
    except ValueError as exc:
        assert str(exc) == "job must not be None"
    else:
        assert False


def test_daily_scheduler_does_not_run_before_schedule_time():
    scheduler = DailyScheduler(
        schedule=DailySchedule(hour=19, minute=0),
        job=lambda: "ok",
    )

    result = scheduler.tick(datetime(2026, 7, 9, 18, 59))

    assert result.should_run is False
    assert result.executed is False
    assert result.data is None
    assert result.error is None
    assert scheduler.last_run_date is None


def test_daily_scheduler_runs_at_schedule_time():
    scheduler = DailyScheduler(
        schedule=DailySchedule(hour=19, minute=0),
        job=lambda: "ok",
    )

    result = scheduler.tick(datetime(2026, 7, 9, 19, 0))

    assert result.should_run is True
    assert result.executed is True
    assert result.data == "ok"
    assert result.error is None
    assert scheduler.last_run_date == datetime(2026, 7, 9).date()


def test_daily_scheduler_runs_after_schedule_time():
    scheduler = DailyScheduler(
        schedule=DailySchedule(hour=19, minute=0),
        job=lambda: "ok",
    )

    result = scheduler.tick(datetime(2026, 7, 9, 20, 30))

    assert result.should_run is True
    assert result.executed is True
    assert result.data == "ok"
    assert result.error is None


def test_daily_scheduler_runs_only_once_per_day():
    count = {"value": 0}

    def job():
        count["value"] += 1
        return count["value"]

    scheduler = DailyScheduler(
        schedule=DailySchedule(hour=19, minute=0),
        job=job,
    )

    first = scheduler.tick(datetime(2026, 7, 9, 19, 0))
    second = scheduler.tick(datetime(2026, 7, 9, 20, 0))

    assert first.executed is True
    assert first.data == 1

    assert second.should_run is False
    assert second.executed is False
    assert second.data is None

    assert count["value"] == 1


def test_daily_scheduler_runs_again_next_day():
    count = {"value": 0}

    def job():
        count["value"] += 1
        return count["value"]

    scheduler = DailyScheduler(
        schedule=DailySchedule(hour=19, minute=0),
        job=job,
    )

    first = scheduler.tick(datetime(2026, 7, 9, 19, 0))
    second = scheduler.tick(datetime(2026, 7, 10, 19, 0))

    assert first.executed is True
    assert first.data == 1

    assert second.executed is True
    assert second.data == 2

    assert count["value"] == 2


def test_daily_scheduler_returns_error_when_job_fails():
    def job():
        raise RuntimeError("job failed")

    scheduler = DailyScheduler(
        schedule=DailySchedule(hour=19, minute=0),
        job=job,
    )

    result = scheduler.tick(datetime(2026, 7, 9, 19, 0))

    assert result.should_run is True
    assert result.executed is False
    assert result.data is None
    assert result.error == "job failed"
    assert scheduler.last_run_date is None