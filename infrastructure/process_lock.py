from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


class ProcessFileLock:
    """
    File lock ngăn nhiều DMI production process
    chạy đồng thời.

    Cơ chế:
    - tạo file lock bằng O_CREAT | O_EXCL
    - thao tác tạo file là atomic
    - lưu PID, timestamp và ownership token
    - tự dọn lock quá hạn
    - chỉ process sở hữu token mới được release

    Lock mặc định được coi là stale sau 6 giờ.
    """

    DEFAULT_STALE_AFTER_SECONDS = 6 * 60 * 60

    def __init__(
        self,
        lock_path: str | Path,
        stale_after_seconds: float = (
            DEFAULT_STALE_AFTER_SECONDS
        ),
        clock: Any | None = None,
    ) -> None:
        if lock_path is None or not str(
            lock_path
        ).strip():
            raise ValueError(
                "lock_path must not be empty"
            )

        normalized_stale_after_seconds = float(
            stale_after_seconds
        )

        if normalized_stale_after_seconds <= 0:
            raise ValueError(
                "stale_after_seconds must be "
                "greater than 0"
            )

        self._lock_path = Path(
            str(lock_path).strip()
        )

        self._stale_after_seconds = (
            normalized_stale_after_seconds
        )

        self._clock = clock
        self._token: str | None = None
        self._acquired = False

    @property
    def lock_path(self) -> str:
        return str(self._lock_path)

    @property
    def acquired(self) -> bool:
        return self._acquired

    def acquire(self) -> bool:
        """
        Thử chiếm lock.

        Returns:
            True nếu chiếm lock thành công.
            False nếu đang có process khác giữ lock.
        """

        if self._acquired:
            return True

        self._lock_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        token = uuid.uuid4().hex

        if self._try_create_lock(token):
            self._token = token
            self._acquired = True

            return True

        if not self._is_stale():
            return False

        self._remove_stale_lock()

        if self._try_create_lock(token):
            self._token = token
            self._acquired = True

            return True

        return False

    def release(self) -> None:
        """
        Giải phóng lock nếu instance hiện tại sở hữu lock.
        """

        if not self._acquired:
            return

        try:
            current_token = self._read_token()

            if (
                current_token is not None
                and current_token == self._token
                and self._lock_path.exists()
            ):
                self._lock_path.unlink()

        finally:
            self._token = None
            self._acquired = False

    def __enter__(
        self,
    ) -> ProcessFileLock:
        if not self.acquire():
            raise RuntimeError(
                "process lock is already acquired"
            )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.release()

    def _try_create_lock(
        self,
        token: str,
    ) -> bool:
        flags = (
            os.O_CREAT
            | os.O_EXCL
            | os.O_WRONLY
        )

        try:
            file_descriptor = os.open(
                str(self._lock_path),
                flags,
            )

        except FileExistsError:
            return False

        try:
            metadata = {
                "pid": os.getpid(),
                "token": token,
                "acquired_at": (
                    self._now().isoformat()
                ),
            }

            raw_content = json.dumps(
                metadata,
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8")

            os.write(
                file_descriptor,
                raw_content,
            )

        finally:
            os.close(file_descriptor)

        return True

    def _is_stale(self) -> bool:
        if not self._lock_path.exists():
            return False

        try:
            modified_at = (
                self._lock_path.stat().st_mtime
            )

        except FileNotFoundError:
            return False

        age_seconds = max(
            0.0,
            time.time() - modified_at,
        )

        return (
            age_seconds
            >= self._stale_after_seconds
        )

    def _remove_stale_lock(self) -> None:
        try:
            self._lock_path.unlink()

        except FileNotFoundError:
            pass

    def _read_token(self) -> str | None:
        if not self._lock_path.exists():
            return None

        try:
            content = self._lock_path.read_text(
                encoding="utf-8"
            )

            data = json.loads(content)

            token = data.get("token")

            if token is None:
                return None

            normalized_token = str(token).strip()

            return normalized_token or None

        except (
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ):
            return None

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