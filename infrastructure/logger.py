from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, TextIO
import sys


class SimpleLogger:
    """
    Logger đơn giản cho DMI.

    Hỗ trợ:
    - ghi console
    - ghi file theo ngày
    - inject output để test
    - inject clock để test
    - tự tạo thư mục log

    Cấu trúc file mặc định:

    logs/
        runtime/
            YYYY/
                MM/
                    DD.log

    Backward compatibility:

    SimpleLogger()

    vẫn ghi console giống phiên bản cũ.
    """

    def __init__(
        self,
        output: TextIO | None = None,
        log_directory: str | Path | None = None,
        enable_console: bool = True,
        enable_file: bool = False,
        clock: Any | None = None,
        encoding: str = "utf-8",
    ) -> None:
        if output is not None and not hasattr(
            output,
            "write",
        ):
            raise TypeError(
                "output must have write method"
            )

        if encoding is None or not str(encoding).strip():
            raise ValueError(
                "encoding must not be empty"
            )

        self._output = output or sys.stdout

        self._log_directory = (
            Path(log_directory)
            if log_directory is not None
            else Path("logs") / "runtime"
        )

        self._enable_console = bool(enable_console)
        self._enable_file = bool(enable_file)
        self._clock = clock
        self._encoding = str(encoding).strip()

    @property
    def log_directory(self) -> str:
        return str(self._log_directory)

    @property
    def enable_console(self) -> bool:
        return self._enable_console

    @property
    def enable_file(self) -> bool:
        return self._enable_file

    def info(
        self,
        message: str,
    ) -> None:
        self._log(
            level="INFO",
            message=message,
        )

    def warning(
        self,
        message: str,
    ) -> None:
        self._log(
            level="WARNING",
            message=message,
        )

    def error(
        self,
        message: str,
    ) -> None:
        self._log(
            level="ERROR",
            message=message,
        )

    def startup(
        self,
        application_name: str,
        version: str,
        environment: str,
    ) -> None:
        normalized_application_name = (
            self._normalize_required_text(
                value=application_name,
                field_name="application_name",
            )
        )

        normalized_version = (
            self._normalize_required_text(
                value=version,
                field_name="version",
            )
        )

        normalized_environment = (
            self._normalize_required_text(
                value=environment,
                field_name="environment",
            )
        )

        separator = "=" * 50

        self.info(separator)
        self.info(normalized_application_name)
        self.info(f"Version: {normalized_version}")
        self.info(
            f"Environment: {normalized_environment}"
        )
        self.info("Daily production started")
        self.info(separator)

    def shutdown(
        self,
        exit_code: int,
        elapsed_seconds: float,
    ) -> None:
        normalized_exit_code = int(exit_code)
        normalized_elapsed_seconds = float(
            elapsed_seconds
        )

        if normalized_elapsed_seconds < 0:
            raise ValueError(
                "elapsed_seconds must not be negative"
            )

        separator = "=" * 50

        self.info(separator)
        self.info(
            "Daily production completed "
            f"with exit code {normalized_exit_code}"
        )
        self.info(
            "Elapsed: "
            f"{normalized_elapsed_seconds:.3f} seconds"
        )
        self.info("DMI shutdown completed")
        self.info(separator)

    def get_log_file_path(self) -> str:
        current_time = self._now()

        file_path = (
            self._log_directory
            / current_time.strftime("%Y")
            / current_time.strftime("%m")
            / f"{current_time.strftime('%d')}.log"
        )

        return str(file_path)

    def _log(
        self,
        level: str,
        message: str,
    ) -> None:
        normalized_level = (
            self._normalize_required_text(
                value=level,
                field_name="level",
            ).upper()
        )

        normalized_message = (
            self._normalize_required_text(
                value=message,
                field_name="message",
            )
        )

        formatted_message = self._format(
            level=normalized_level,
            message=normalized_message,
        )

        if self._enable_console:
            self._write_console(
                formatted_message
            )

        if self._enable_file:
            self._write_file(
                formatted_message
            )

    def _write_console(
        self,
        formatted_message: str,
    ) -> None:
        self._output.write(
            f"{formatted_message}\n"
        )

        if hasattr(
            self._output,
            "flush",
        ):
            self._output.flush()

    def _write_file(
        self,
        formatted_message: str,
    ) -> None:
        file_path = Path(
            self.get_log_file_path()
        )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with file_path.open(
            mode="a",
            encoding=self._encoding,
            newline="",
        ) as log_file:
            log_file.write(
                f"{formatted_message}\n"
            )

    def _format(
        self,
        level: str,
        message: str,
    ) -> str:
        timestamp = self._now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            f"[{timestamp}] "
            f"[{level}] "
            f"{message}"
        )

    def _normalize_required_text(
        self,
        value: str,
        field_name: str,
    ) -> str:
        if value is None or not str(value).strip():
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return str(value).strip()

    def _now(self) -> datetime:
        if self._clock is None:
            return datetime.now()

        if not hasattr(
            self._clock,
            "now",
        ):
            raise AttributeError(
                "clock must have now method"
            )

        value = self._clock.now()

        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                "clock.now must return datetime"
            )

        return value