from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any, TextIO

from apps.exit_codes import (
    EXIT_ALREADY_RUNNING,
    EXIT_CLIENT_FAILURE,
    EXIT_CONFIGURATION_ERROR,
    EXIT_RUNTIME_ERROR,
    EXIT_SUCCESS,
)
from infrastructure.logger import SimpleLogger


class DailyApplicationRuntime:
    """
    Runtime điều khiển Daily Production của DMI.

    Responsibility:
    - chiếm production process lock
    - bootstrap application
    - resolve DailyProductionRunner
    - chạy Runner
    - ghi nhật ký vận hành
    - chuyển kết quả thành exit code
    - giải phóng process lock

    Không:
    - đọc CSV trực tiếp
    - phân tích Portfolio
    - render báo cáo
    - gửi Telegram trực tiếp
    - chạy Scheduler
    """

    APPLICATION_NAME = "DMI PLATFORM"
    VERSION = "1.0.0"
    ENVIRONMENT = "PRODUCTION"

    def __init__(
        self,
        application_builder: Callable[[], Any],
        output: TextIO | None = None,
        clock: Any | None = None,
        logger: Any | None = None,
        log_directory: str | None = None,
        enable_file_logging: bool = False,
        process_lock: Any | None = None,
    ) -> None:
        if application_builder is None:
            raise ValueError(
                "application_builder must not be None"
            )

        self._application_builder = (
            application_builder
        )

        self._logger = (
            logger
            or SimpleLogger(
                output=output,
                log_directory=log_directory,
                enable_console=True,
                enable_file=enable_file_logging,
                clock=clock,
            )
        )

        self._process_lock = process_lock

    def run(self) -> int:
        started_at = perf_counter()

        self._logger.startup(
            application_name=self.APPLICATION_NAME,
            version=self.VERSION,
            environment=self.ENVIRONMENT,
        )

        if not self._acquire_process_lock():
            exit_code = EXIT_ALREADY_RUNNING

            self._logger.warning(
                "Another DMI daily production "
                "process is already running"
            )

            self._shutdown(
                exit_code=exit_code,
                started_at=started_at,
            )

            return exit_code

        try:
            return self._run_pipeline(
                started_at=started_at
            )

        finally:
            self._release_process_lock()

    def _run_pipeline(
        self,
        started_at: float,
    ) -> int:
        try:
            application = self._build_application()

        except ValueError as exc:
            exit_code = EXIT_CONFIGURATION_ERROR

            self._logger.error(
                f"Configuration error: {exc}"
            )

            self._shutdown(
                exit_code=exit_code,
                started_at=started_at,
            )

            return exit_code

        except Exception as exc:
            exit_code = EXIT_RUNTIME_ERROR

            self._logger.error(
                f"Bootstrap error: {exc}"
            )

            self._shutdown(
                exit_code=exit_code,
                started_at=started_at,
            )

            return exit_code

        try:
            runner = self._resolve_runner(
                application
            )

            self._logger.info(
                "DailyProductionRunner resolved"
            )

            result = runner.run()

            exit_code = self._resolve_exit_code(
                result
            )

            self._write_result_summary(
                result
            )

            self._shutdown(
                exit_code=exit_code,
                started_at=started_at,
            )

            return exit_code

        except Exception as exc:
            exit_code = EXIT_RUNTIME_ERROR

            self._logger.error(
                f"Runtime error: {exc}"
            )

            self._shutdown(
                exit_code=exit_code,
                started_at=started_at,
            )

            return exit_code

    def _acquire_process_lock(self) -> bool:
        if self._process_lock is None:
            return True

        if not hasattr(
            self._process_lock,
            "acquire",
        ):
            raise AttributeError(
                "process_lock must have acquire method"
            )

        acquired = bool(
            self._process_lock.acquire()
        )

        if acquired:
            self._logger.info(
                "Production process lock acquired"
            )

        return acquired

    def _release_process_lock(self) -> None:
        if self._process_lock is None:
            return

        if not hasattr(
            self._process_lock,
            "release",
        ):
            self._logger.warning(
                "Process lock does not have "
                "release method"
            )

            return

        try:
            self._process_lock.release()

            self._logger.info(
                "Production process lock released"
            )

        except Exception as exc:
            self._logger.warning(
                f"Failed to release process lock: {exc}"
            )

    def _build_application(self) -> Any:
        self._logger.info(
            "Building application container"
        )

        application = self._application_builder()

        if application is None:
            raise RuntimeError(
                "application_builder returned None"
            )

        self._logger.info(
            "Application container built successfully"
        )

        return application

    def _resolve_runner(
        self,
        application: Any,
    ) -> Any:
        if not hasattr(
            application,
            "daily_production_runner",
        ):
            raise AttributeError(
                "application must have "
                "daily_production_runner"
            )

        runner = (
            application.daily_production_runner
        )

        if runner is None:
            raise RuntimeError(
                "daily_production_runner "
                "is not configured"
            )

        if not hasattr(
            runner,
            "run",
        ):
            raise AttributeError(
                "daily_production_runner "
                "must have run method"
            )

        return runner

    def _resolve_exit_code(
        self,
        result: Any,
    ) -> int:
        if result is None:
            raise RuntimeError(
                "daily production runner "
                "returned None"
            )

        runner_error = getattr(
            result,
            "error",
            None,
        )

        if (
            runner_error is not None
            and str(runner_error).strip()
        ):
            return EXIT_RUNTIME_ERROR

        failure_count = int(
            getattr(
                result,
                "failure_count",
                0,
            )
        )

        if failure_count > 0:
            return EXIT_CLIENT_FAILURE

        succeeded = bool(
            getattr(
                result,
                "succeeded",
                False,
            )
        )

        if not succeeded:
            return EXIT_RUNTIME_ERROR

        return EXIT_SUCCESS

    def _write_result_summary(
        self,
        result: Any,
    ) -> None:
        total_count = int(
            getattr(
                result,
                "total_count",
                0,
            )
        )

        success_count = int(
            getattr(
                result,
                "success_count",
                0,
            )
        )

        failure_count = int(
            getattr(
                result,
                "failure_count",
                0,
            )
        )

        self._logger.info(
            f"Clients processed: {total_count}"
        )

        self._logger.info(
            f"Clients succeeded: {success_count}"
        )

        if failure_count > 0:
            self._logger.warning(
                f"Clients failed: {failure_count}"
            )
        else:
            self._logger.info(
                "Clients failed: 0"
            )

        message = getattr(
            result,
            "message",
            None,
        )

        if (
            message is not None
            and str(message).strip()
        ):
            self._logger.info(
                str(message).strip()
            )

        runner_error = getattr(
            result,
            "error",
            None,
        )

        if (
            runner_error is not None
            and str(runner_error).strip()
        ):
            self._logger.error(
                "Runner error: "
                f"{str(runner_error).strip()}"
            )

        results = getattr(
            result,
            "results",
            (),
        )

        if results is None:
            return

        total_results = len(results)

        for index, client_result in enumerate(
            results,
            start=1,
        ):
            client_id = str(
                getattr(
                    client_result,
                    "client_id",
                    "UNKNOWN",
                )
            ).strip() or "UNKNOWN"

            success = bool(
                getattr(
                    client_result,
                    "success",
                    False,
                )
            )

            if success:
                self._logger.info(
                    f"[{index}/{total_results}] "
                    f"Client {client_id}: SUCCESS"
                )

                continue

            error = str(
                getattr(
                    client_result,
                    "error",
                    "unknown client error",
                )
            ).strip() or "unknown client error"

            self._logger.error(
                f"[{index}/{total_results}] "
                f"Client {client_id}: FAILED - "
                f"{error}"
            )

    def _shutdown(
        self,
        exit_code: int,
        started_at: float,
    ) -> None:
        elapsed_seconds = max(
            0.0,
            perf_counter() - started_at,
        )

        self._logger.shutdown(
            exit_code=exit_code,
            elapsed_seconds=elapsed_seconds,
        )