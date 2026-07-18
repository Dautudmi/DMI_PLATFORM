from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from typing import Any

import pytest

from apps.exit_codes import (
    EXIT_CLIENT_FAILURE,
    EXIT_CONFIGURATION_ERROR,
    EXIT_RUNTIME_ERROR,
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
            13,
            19,
            0,
            0,
        )


@dataclass
class FakeClientResult:
    success: bool
    client_id: str
    error: str | None = None


@dataclass
class FakeRunnerResult:
    succeeded: bool
    total_count: int
    success_count: int
    failure_count: int

    results: tuple[
        FakeClientResult,
        ...,
    ] = ()

    message: str | None = None
    error: str | None = None


class FakeRunner:
    def __init__(
        self,
        result: Any = None,
        error: Exception | None = None,
    ) -> None:
        self._result = result
        self._error = error
        self.call_count = 0

    def run(self) -> Any:
        self.call_count += 1

        if self._error is not None:
            raise self._error

        return self._result


class FakeApplication:
    def __init__(
        self,
        runner: Any,
    ) -> None:
        self.daily_production_runner = runner


def create_runtime(
    builder,
) -> tuple[
    DailyApplicationRuntime,
    StringIO,
]:
    output = StringIO()

    runtime = DailyApplicationRuntime(
        application_builder=builder,
        output=output,
        clock=FixedClock(),
    )

    return runtime, output


def test_constructor_rejects_none_builder() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "application_builder "
            "must not be None"
        ),
    ):
        DailyApplicationRuntime(
            application_builder=None
        )


def test_success_returns_zero() -> None:
    runner_result = FakeRunnerResult(
        succeeded=True,
        total_count=2,
        success_count=2,
        failure_count=0,
        message=(
            "Daily production completed: "
            "2 succeeded, 0 failed"
        ),
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS
    assert runner.call_count == 1

    text = output.getvalue()

    assert "DMI PLATFORM" in text
    assert "Version: 1.0.0" in text
    assert "Environment: PRODUCTION" in text
    assert "Daily production started" in text

    assert (
        "Building application container"
        in text
    )

    assert (
        "Application container built successfully"
        in text
    )

    assert (
        "DailyProductionRunner resolved"
        in text
    )

    assert "Clients processed: 2" in text
    assert "Clients succeeded: 2" in text
    assert "Clients failed: 0" in text

    assert (
        "Daily production completed: "
        "2 succeeded, 0 failed"
        in text
    )

    assert "exit code 0" in text
    assert "DMI shutdown completed" in text


def test_configuration_error_returns_ten() -> None:
    def broken_builder() -> Any:
        raise ValueError(
            "Missing required config"
        )

    runtime, output = create_runtime(
        builder=broken_builder
    )

    exit_code = runtime.run()

    assert (
        exit_code
        == EXIT_CONFIGURATION_ERROR
    )

    text = output.getvalue()

    assert (
        "Configuration error: "
        "Missing required config"
        in text
    )

    assert "exit code 10" in text
    assert "DMI shutdown completed" in text


def test_bootstrap_error_returns_twenty() -> None:
    def broken_builder() -> Any:
        raise RuntimeError(
            "container creation failed"
        )

    runtime, output = create_runtime(
        builder=broken_builder
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "Bootstrap error: "
        "container creation failed"
        in text
    )

    assert "exit code 20" in text
    assert "DMI shutdown completed" in text


def test_client_failure_returns_thirty() -> None:
    failed_client = FakeClientResult(
        success=False,
        client_id="anh_dung",
        error="portfolio file not found",
    )

    runner_result = FakeRunnerResult(
        succeeded=False,
        total_count=2,
        success_count=1,
        failure_count=1,
        results=(failed_client,),
        message=(
            "Daily production completed: "
            "1 succeeded, 1 failed"
        ),
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert (
        exit_code
        == EXIT_CLIENT_FAILURE
    )

    text = output.getvalue()

    assert "Clients processed: 2" in text
    assert "Clients succeeded: 1" in text
    assert "Clients failed: 1" in text

    assert (
        "Daily production completed: "
        "1 succeeded, 1 failed"
        in text
    )

    assert (
        "[1/1] Client anh_dung: FAILED - "
        "portfolio file not found"
        in text
    )

    assert "exit code 30" in text
    assert "DMI shutdown completed" in text


def test_successful_client_is_logged() -> None:
    successful_client = FakeClientResult(
        success=True,
        client_id="anh_manh",
        error=None,
    )

    runner_result = FakeRunnerResult(
        succeeded=True,
        total_count=1,
        success_count=1,
        failure_count=0,
        results=(successful_client,),
        message=(
            "Daily production completed: "
            "1 succeeded, 0 failed"
        ),
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS

    text = output.getvalue()

    assert (
        "[1/1] Client anh_manh: SUCCESS"
        in text
    )


def test_mixed_clients_are_logged_with_progress() -> None:
    successful_client = FakeClientResult(
        success=True,
        client_id="anh_manh",
    )

    failed_client = FakeClientResult(
        success=False,
        client_id="chi_binh",
        error="analysis failed",
    )

    runner_result = FakeRunnerResult(
        succeeded=False,
        total_count=2,
        success_count=1,
        failure_count=1,
        results=(
            successful_client,
            failed_client,
        ),
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert (
        exit_code
        == EXIT_CLIENT_FAILURE
    )

    text = output.getvalue()

    assert (
        "[1/2] Client anh_manh: SUCCESS"
        in text
    )

    assert (
        "[2/2] Client chi_binh: FAILED - "
        "analysis failed"
        in text
    )


def test_runner_error_returns_twenty() -> None:
    runner_result = FakeRunnerResult(
        succeeded=False,
        total_count=0,
        success_count=0,
        failure_count=0,
        error="client registry unavailable",
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "Runner error: "
        "client registry unavailable"
        in text
    )

    assert "exit code 20" in text
    assert "DMI shutdown completed" in text


def test_runner_exception_returns_twenty() -> None:
    runner = FakeRunner(
        error=RuntimeError(
            "unexpected runner failure"
        )
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "Runtime error: "
        "unexpected runner failure"
        in text
    )

    assert "exit code 20" in text
    assert "DMI shutdown completed" in text


def test_missing_runner_returns_twenty() -> None:
    application = FakeApplication(
        runner=None
    )

    runtime, output = create_runtime(
        builder=lambda: application
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "daily_production_runner "
        "is not configured"
        in text
    )

    assert "exit code 20" in text


def test_application_without_runner_attribute_returns_twenty() -> None:
    class ApplicationWithoutRunner:
        pass

    runtime, output = create_runtime(
        builder=lambda: ApplicationWithoutRunner()
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "application must have "
        "daily_production_runner"
        in text
    )


def test_runner_without_run_method_returns_twenty() -> None:
    class RunnerWithoutRun:
        pass

    application = FakeApplication(
        runner=RunnerWithoutRun()
    )

    runtime, output = create_runtime(
        builder=lambda: application
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "daily_production_runner "
        "must have run method"
        in text
    )


def test_builder_returning_none_returns_twenty() -> None:
    runtime, output = create_runtime(
        builder=lambda: None
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "application_builder returned None"
        in text
    )

    assert "exit code 20" in text


def test_runner_returning_none_returns_twenty() -> None:
    runner = FakeRunner(
        result=None
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    text = output.getvalue()

    assert (
        "daily production runner "
        "returned None"
        in text
    )

    assert "exit code 20" in text


def test_unsuccessful_result_without_failures_returns_twenty() -> None:
    runner_result = FakeRunnerResult(
        succeeded=False,
        total_count=0,
        success_count=0,
        failure_count=0,
        results=(),
        message=None,
        error=None,
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_RUNTIME_ERROR

    assert "exit code 20" in (
        output.getvalue()
    )


def test_output_contains_fixed_timestamp() -> None:
    runner_result = FakeRunnerResult(
        succeeded=True,
        total_count=0,
        success_count=0,
        failure_count=0,
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS

    assert (
        "[2026-07-13 19:00:00]"
        in output.getvalue()
    )


def test_output_contains_log_levels() -> None:
    runner_result = FakeRunnerResult(
        succeeded=True,
        total_count=0,
        success_count=0,
        failure_count=0,
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS

    text = output.getvalue()

    assert "[INFO]" in text


def test_configuration_error_uses_error_level() -> None:
    def broken_builder() -> Any:
        raise ValueError(
            "invalid configuration"
        )

    runtime, output = create_runtime(
        builder=broken_builder
    )

    exit_code = runtime.run()

    assert (
        exit_code
        == EXIT_CONFIGURATION_ERROR
    )

    text = output.getvalue()

    assert (
        "[ERROR] Configuration error: "
        "invalid configuration"
        in text
    )


def test_client_failure_count_uses_warning_level() -> None:
    failed_client = FakeClientResult(
        success=False,
        client_id="anh_dung",
        error="portfolio missing",
    )

    runner_result = FakeRunnerResult(
        succeeded=False,
        total_count=1,
        success_count=0,
        failure_count=1,
        results=(failed_client,),
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert (
        exit_code
        == EXIT_CLIENT_FAILURE
    )

    text = output.getvalue()

    assert (
        "[WARNING] Clients failed: 1"
        in text
    )

    assert (
        "[ERROR] [1/1] Client anh_dung: "
        "FAILED - portfolio missing"
        in text
    )


def test_shutdown_contains_elapsed_time() -> None:
    runner_result = FakeRunnerResult(
        succeeded=True,
        total_count=0,
        success_count=0,
        failure_count=0,
    )

    runner = FakeRunner(
        result=runner_result
    )

    runtime, output = create_runtime(
        builder=lambda: FakeApplication(
            runner=runner
        )
    )

    exit_code = runtime.run()

    assert exit_code == EXIT_SUCCESS

    text = output.getvalue()

    assert "Elapsed:" in text
    assert "seconds" in text