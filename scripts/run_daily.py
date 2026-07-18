from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from apps.bootstrap import build_application
from apps.runtime import DailyApplicationRuntime
from infrastructure.process_lock import (
    ProcessFileLock,
)


def main() -> int:
    """
    Entry point cho DMI Daily Production.

    Windows Task Scheduler:

    python scripts/run_daily.py
    """

    process_lock = ProcessFileLock(
        lock_path=(
            PROJECT_ROOT
            / "runtime"
            / "locks"
            / "daily_production.lock"
        ),
        stale_after_seconds=6 * 60 * 60,
    )

    runtime = DailyApplicationRuntime(
        application_builder=build_application,
        log_directory=(
            PROJECT_ROOT
            / "logs"
            / "runtime"
        ),
        enable_file_logging=True,
        process_lock=process_lock,
    )

    return runtime.run()


if __name__ == "__main__":
    raise SystemExit(main())