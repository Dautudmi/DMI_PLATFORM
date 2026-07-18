from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path

import pytest

from infrastructure.logger import (
    SimpleLogger,
)


class FixedClock:
    def now(self) -> datetime:
        return datetime(
            2026,
            7,
            13,
            19,
            0,
            1,
        )


def test_info_writes_console() -> None:
    output = StringIO()

    logger = SimpleLogger(
        output=output,
        clock=FixedClock(),
    )

    logger.info("Application started")

    assert output.getvalue() == (
        "[2026-07-13 19:00:01] "
        "[INFO] "
        "Application started\n"
    )


def test_warning_writes_console() -> None:
    output = StringIO()

    logger = SimpleLogger(
        output=output,
        clock=FixedClock(),
    )

    logger.warning("Client failed")

    assert "[WARNING] Client failed" in (
        output.getvalue()
    )


def test_error_writes_console() -> None:
    output = StringIO()

    logger = SimpleLogger(
        output=output,
        clock=FixedClock(),
    )

    logger.error("Runtime failure")

    assert "[ERROR] Runtime failure" in (
        output.getvalue()
    )


def test_file_logging_creates_daily_file(
    tmp_path: Path,
) -> None:
    logger = SimpleLogger(
        output=StringIO(),
        log_directory=tmp_path,
        enable_console=False,
        enable_file=True,
        clock=FixedClock(),
    )

    logger.info("File log message")

    expected_path = (
        tmp_path
        / "2026"
        / "07"
        / "13.log"
    )

    assert expected_path.is_file()

    content = expected_path.read_text(
        encoding="utf-8"
    )

    assert "[INFO] File log message" in content


def test_file_logging_appends_messages(
    tmp_path: Path,
) -> None:
    logger = SimpleLogger(
        output=StringIO(),
        log_directory=tmp_path,
        enable_console=False,
        enable_file=True,
        clock=FixedClock(),
    )

    logger.info("First message")
    logger.error("Second message")

    expected_path = (
        tmp_path
        / "2026"
        / "07"
        / "13.log"
    )

    content = expected_path.read_text(
        encoding="utf-8"
    )

    assert "First message" in content
    assert "Second message" in content

    assert content.count(
        "2026-07-13 19:00:01"
    ) == 2


def test_console_and_file_logging_together(
    tmp_path: Path,
) -> None:
    output = StringIO()

    logger = SimpleLogger(
        output=output,
        log_directory=tmp_path,
        enable_console=True,
        enable_file=True,
        clock=FixedClock(),
    )

    logger.info("Production message")

    assert "Production message" in (
        output.getvalue()
    )

    expected_path = (
        tmp_path
        / "2026"
        / "07"
        / "13.log"
    )

    assert "Production message" in (
        expected_path.read_text(
            encoding="utf-8"
        )
    )


def test_startup_writes_banner() -> None:
    output = StringIO()

    logger = SimpleLogger(
        output=output,
        clock=FixedClock(),
    )

    logger.startup(
        application_name="DMI PLATFORM",
        version="1.0.0",
        environment="PRODUCTION",
    )

    text = output.getvalue()

    assert "DMI PLATFORM" in text
    assert "Version: 1.0.0" in text
    assert "Environment: PRODUCTION" in text
    assert "Daily production started" in text


def test_shutdown_writes_summary() -> None:
    output = StringIO()

    logger = SimpleLogger(
        output=output,
        clock=FixedClock(),
    )

    logger.shutdown(
        exit_code=0,
        elapsed_seconds=1.23456,
    )

    text = output.getvalue()

    assert "exit code 0" in text
    assert "Elapsed: 1.235 seconds" in text
    assert "DMI shutdown completed" in text


def test_shutdown_rejects_negative_elapsed() -> None:
    logger = SimpleLogger(
        output=StringIO(),
        clock=FixedClock(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "elapsed_seconds must not be negative"
        ),
    ):
        logger.shutdown(
            exit_code=0,
            elapsed_seconds=-1,
        )


def test_rejects_empty_message() -> None:
    logger = SimpleLogger(
        output=StringIO(),
        clock=FixedClock(),
    )

    with pytest.raises(
        ValueError,
        match="message must not be empty",
    ):
        logger.info("   ")


def test_get_log_file_path() -> None:
    logger = SimpleLogger(
        output=StringIO(),
        log_directory="runtime_logs",
        clock=FixedClock(),
    )

    expected = str(
        Path("runtime_logs")
        / "2026"
        / "07"
        / "13.log"
    )

    assert (
        logger.get_log_file_path()
        == expected
    )