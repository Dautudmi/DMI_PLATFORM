from __future__ import annotations

from typing import Any

from apps.portfolio.models.daily_production_runner_result import (
    DailyProductionRunnerResult,
)
from apps.portfolio.models.telegram_delivery_item_result import (
    TelegramDeliveryItemResult,
)
from apps.portfolio.models.telegram_delivery_result import (
    TelegramDeliveryResult,
)
from presentation.telegram.telegram_message import (
    TelegramMessage,
)
from presentation.telegram.telegram_send_result import (
    TelegramSendResult,
)


class TelegramDeliveryService:
    """
    Application Service gửi các báo cáo Daily Production
    lên Telegram.

    Flow:

    DailyProductionRunnerResult
        ↓
    successful_results
        ↓
    TelegramMessage
        ↓
    TelegramSender.send_message()
        ↓
    TelegramDeliveryResult

    Responsibility:
    - lọc các client có report thành công
    - tạo TelegramMessage cho từng client
    - gọi TelegramSender hiện có
    - cô lập lỗi gửi của từng client
    - tổng hợp kết quả delivery

    Không:
    - chạy DailyProductionRunner
    - đọc Portfolio
    - build hoặc render PortfolioReport
    - thay đổi DailyProductionRunnerResult
    - quyết định exit code production
    """

    def __init__(
        self,
        telegram_sender: Any,
        enabled: bool = False,
        parse_mode: str | None = "Markdown",
        disable_web_page_preview: bool = True,
    ) -> None:
        if telegram_sender is None:
            raise ValueError(
                "telegram_sender must not be None"
            )

        self._telegram_sender = telegram_sender
        self._enabled = bool(enabled)

        self._parse_mode = (
            self._normalize_optional_text(
                parse_mode
            )
        )

        self._disable_web_page_preview = bool(
            disable_web_page_preview
        )

    @property
    def enabled(self) -> bool:
        return self._enabled

    def deliver(
        self,
        production_result: DailyProductionRunnerResult,
        chat_id: str,
    ) -> TelegramDeliveryResult:
        """
        Gửi tất cả report thành công tới một chat_id.

        Đây là chế độ Broker/Admin chat chung.

        Việc ánh xạ từng client sang chat_id riêng sẽ được
        bổ sung ở Sprint sau khi format cấu hình được chốt.
        """

        if production_result is None:
            raise ValueError(
                "production_result must not be None"
            )

        normalized_chat_id = (
            self._normalize_required_text(
                value=chat_id,
                field_name="chat_id",
            )
        )

        if not self._enabled:
            return TelegramDeliveryResult(
                enabled=False,
                results=(),
                message="Telegram delivery is disabled",
                error=None,
            )

        try:
            successful_results = tuple(
                production_result.successful_results
            )

        except Exception as exc:
            return TelegramDeliveryResult(
                enabled=True,
                results=(),
                message=None,
                error=str(exc),
            )

        delivery_results: list[
            TelegramDeliveryItemResult
        ] = []

        for client_result in successful_results:
            delivery_result = self._deliver_client_safely(
                client_result=client_result,
                chat_id=normalized_chat_id,
            )

            delivery_results.append(
                delivery_result
            )

        normalized_results = tuple(
            delivery_results
        )

        success_count = sum(
            1
            for result in normalized_results
            if result.success
        )

        failure_count = (
            len(normalized_results) - success_count
        )

        if not normalized_results:
            message = (
                "Telegram delivery completed: "
                "no successful client reports"
            )

        else:
            message = (
                "Telegram delivery completed: "
                f"{success_count} sent, "
                f"{failure_count} failed"
            )

        return TelegramDeliveryResult(
            enabled=True,
            results=normalized_results,
            message=message,
            error=None,
        )

    def _deliver_client_safely(
        self,
        client_result: Any,
        chat_id: str,
    ) -> TelegramDeliveryItemResult:
        client_id = self._resolve_client_id(
            client_result
        )

        try:
            report_text = self._resolve_report_text(
                client_result
            )

            message = TelegramMessage(
                title=(
                    f"📊 DMI REPORT — {client_id}"
                ),
                body=report_text,
                parse_mode=self._parse_mode,
            )

            send_result = self._send_message(
                chat_id=chat_id,
                message=message,
            )

            if not send_result.success:
                return TelegramDeliveryItemResult(
                    success=False,
                    client_id=client_id,
                    chat_id=chat_id,
                    send_result=send_result,
                    error=(
                        send_result.error
                        or "Telegram send failed"
                    ),
                )

            return TelegramDeliveryItemResult(
                success=True,
                client_id=client_id,
                chat_id=chat_id,
                send_result=send_result,
                error=None,
            )

        except Exception as exc:
            return TelegramDeliveryItemResult(
                success=False,
                client_id=client_id,
                chat_id=chat_id,
                send_result=None,
                error=str(exc),
            )

    def _send_message(
        self,
        chat_id: str,
        message: TelegramMessage,
    ) -> TelegramSendResult:
        sender = self._telegram_sender

        if not hasattr(
            sender,
            "send_message",
        ):
            raise AttributeError(
                "telegram_sender must have "
                "send_message method"
            )

        result = sender.send_message(
            chat_id=chat_id,
            text=message.text,
            parse_mode=message.parse_mode,
            disable_web_page_preview=(
                self._disable_web_page_preview
            ),
        )

        if not isinstance(
            result,
            TelegramSendResult,
        ):
            raise TypeError(
                "telegram_sender.send_message must return "
                "TelegramSendResult"
            )

        return result

    def _resolve_client_id(
        self,
        client_result: Any,
    ) -> str:
        client_id = getattr(
            client_result,
            "client_id",
            None,
        )

        return self._normalize_required_text(
            value=client_id,
            field_name="client_result.client_id",
        )

    def _resolve_report_text(
        self,
        client_result: Any,
    ) -> str:
        report_text = getattr(
            client_result,
            "report_text",
            None,
        )

        return self._normalize_required_text(
            value=report_text,
            field_name="client_result.report_text",
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