from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from typing import Any

from apps.exit_codes import (
    EXIT_ALREADY_RUNNING,
    EXIT_SUCCESS,
)
from apps.runtime import (
    DailyApplicationRuntime,
)


class FixedClock:
    def now(self) -> datetime:
        return datetime(
            2026,
            7,
            14,
            19,
            0,
            0,
        )


class FakeProcessLock:
    def __init__(
        self,
        acquire_result: bool,
    ) -> None:
        self._acquire_result = (
            acquire_result
        )

        self.acquire_count = 0
        self.release_count = 0

    def acquire(self) -> bool:
        self.acquire_count += 1

        return self._acquire_result

    def release(self) -> None:
        self.release_count += 1


@dataclass
class FakeRunnerResult:
    succeeded: bool = True
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    results: tuple = ()
    message: str | None = None
    error: str | None = None


class FakeRunner:
    def run(self) -> FakeRunnerResult:
        return FakeRunnerResult()


class FakeApplication:
    daily_production_runner = FakeRunner()


def test_runtime_acquires_and_releases_lock() -> None:
    output = StringIO()

    process_lock = FakeProcessLock(
        acquire_result=True
    )

    runtime = DailyApplicationRuntime(
        application_builder=(
            lambda: FakeApplication()
        ),
        output=output,
        clock=FixedClock(),
        process_lock=process_lock,
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS
    assert process_lock.acquire_count == 1
    assert process_lock.release_count == 1

    text = output.getvalue()

    assert (
        "Production process lock acquired"
        in text
    )

    assert (
        "Production process lock released"
        in text
    )


def test_runtime_returns_forty_when_locked() -> None:
    output = StringIO()

    process_lock = FakeProcessLock(
        acquire_result=False
    )

    builder_call_count = 0

    def builder() -> Any:
        nonlocal builder_call_count

        builder_call_count += 1

        return FakeApplication()

    runtime = DailyApplicationRuntime(
        application_builder=builder,
        output=output,
        clock=FixedClock(),
        process_lock=process_lock,
    )

    exit_code = runtime.run()

    assert (
        exit_code
        == EXIT_ALREADY_RUNNING
    )

    assert builder_call_count == 0
    assert process_lock.acquire_count == 1
    assert process_lock.release_count == 0

    text = output.getvalue()

    assert (
        "Another DMI daily production "
        "process is already running"
        in text
    )

    assert "exit code 40" in text


def test_runtime_without_lock_remains_compatible() -> None:
    output = StringIO()

    runtime = DailyApplicationRuntime(
        application_builder=(
            lambda: FakeApplication()
        ),
        output=output,
        clock=FixedClock(),
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS