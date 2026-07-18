from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from infrastructure.process_lock import (
    ProcessFileLock,
)


def test_acquire_creates_lock_file(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    lock = ProcessFileLock(
        lock_path=lock_path
    )

    assert lock.acquire() is True
    assert lock.acquired is True
    assert lock_path.is_file()

    metadata = json.loads(
        lock_path.read_text(
            encoding="utf-8"
        )
    )

    assert metadata["pid"] == os.getpid()
    assert metadata["token"]
    assert metadata["acquired_at"]


def test_second_lock_cannot_acquire(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    first_lock = ProcessFileLock(
        lock_path=lock_path
    )

    second_lock = ProcessFileLock(
        lock_path=lock_path
    )

    assert first_lock.acquire() is True
    assert second_lock.acquire() is False

    first_lock.release()


def test_release_removes_owned_lock(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    lock = ProcessFileLock(
        lock_path=lock_path
    )

    assert lock.acquire() is True

    lock.release()

    assert lock.acquired is False
    assert not lock_path.exists()


def test_release_without_acquire_is_safe(
    tmp_path: Path,
) -> None:
    lock = ProcessFileLock(
        lock_path=(
            tmp_path / "daily.lock"
        )
    )

    lock.release()

    assert lock.acquired is False


def test_same_instance_acquire_is_idempotent(
    tmp_path: Path,
) -> None:
    lock = ProcessFileLock(
        lock_path=(
            tmp_path / "daily.lock"
        )
    )

    assert lock.acquire() is True
    assert lock.acquire() is True

    lock.release()


def test_does_not_remove_foreign_lock(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    lock = ProcessFileLock(
        lock_path=lock_path
    )

    assert lock.acquire() is True

    metadata = json.loads(
        lock_path.read_text(
            encoding="utf-8"
        )
    )

    metadata["token"] = "foreign-token"

    lock_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    lock.release()

    assert lock_path.exists()


def test_stale_lock_is_replaced(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    lock_path.write_text(
        json.dumps(
            {
                "pid": 123,
                "token": "old-token",
                "acquired_at": "2020-01-01",
            }
        ),
        encoding="utf-8",
    )

    old_time = time.time() - 100

    os.utime(
        lock_path,
        (
            old_time,
            old_time,
        ),
    )

    lock = ProcessFileLock(
        lock_path=lock_path,
        stale_after_seconds=10,
    )

    assert lock.acquire() is True

    metadata = json.loads(
        lock_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        metadata["token"]
        != "old-token"
    )

    lock.release()


def test_context_manager_releases_lock(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    lock = ProcessFileLock(
        lock_path=lock_path
    )

    with lock:
        assert lock.acquired is True
        assert lock_path.exists()

    assert lock.acquired is False
    assert not lock_path.exists()


def test_context_manager_rejects_existing_lock(
    tmp_path: Path,
) -> None:
    lock_path = (
        tmp_path / "daily.lock"
    )

    first_lock = ProcessFileLock(
        lock_path=lock_path
    )

    second_lock = ProcessFileLock(
        lock_path=lock_path
    )

    assert first_lock.acquire() is True

    with pytest.raises(
        RuntimeError,
        match=(
            "process lock is already acquired"
        ),
    ):
        with second_lock:
            pass

    first_lock.release()


def test_rejects_empty_lock_path() -> None:
    with pytest.raises(
        ValueError,
        match="lock_path must not be empty",
    ):
        ProcessFileLock(
            lock_path="   "
        )


def test_rejects_invalid_stale_duration(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "stale_after_seconds must be "
            "greater than 0"
        ),
    ):
        ProcessFileLock(
            lock_path=(
                tmp_path / "daily.lock"
            ),
            stale_after_seconds=0,
        )