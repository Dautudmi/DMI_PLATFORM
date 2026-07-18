from __future__ import annotations

from dataclasses import dataclass

from presentation.telegram.telegram_send_result import (
    TelegramSendResult,
)


@dataclass(frozen=True, slots=True)
class TelegramDeliveryItemResult:
    """
    Kết quả gửi báo cáo Telegram của một khách hàng.

    Responsibility:
    - lưu client_id
    - lưu trạng thái gửi
    - lưu TelegramSendResult gốc
    - lưu lỗi delivery nếu có

    Không:
    - gọi Telegram Bot API
    - render báo cáo
    - đọc Portfolio
    - thay đổi kết quả Daily Production
    """

    success: bool
    client_id: str
    chat_id: str

    send_result: TelegramSendResult | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        normalized_client_id = (
            self._normalize_required_text(
                value=self.client_id,
                field_name="client_id",
            )
        )

        normalized_chat_id = (
            self._normalize_required_text(
                value=self.chat_id,
                field_name="chat_id",
            )
        )

        normalized_error = self._normalize_optional_text(
            self.error
        )

        if self.success:
            if self.send_result is None:
                raise ValueError(
                    "send_result is required "
                    "when success is True"
                )

            if not self.send_result.success:
                raise ValueError(
                    "send_result.success must be True "
                    "when success is True"
                )

            if normalized_error is not None:
                raise ValueError(
                    "error must be None "
                    "when success is True"
                )

        object.__setattr__(
            self,
            "client_id",
            normalized_client_id,
        )

        object.__setattr__(
            self,
            "chat_id",
            normalized_chat_id,
        )

        object.__setattr__(
            self,
            "error",
            normalized_error,
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

    def _normalize_optional_text(
        self,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()

        return normalized or None