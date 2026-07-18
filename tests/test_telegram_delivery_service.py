from __future__ import annotations

from typing import Any

import pytest

from apps.portfolio.models.daily_production_client_result import (
    DailyProductionClientResult,
)
from apps.portfolio.models.daily_production_runner_result import (
    DailyProductionRunnerResult,
)
from apps.portfolio.services.telegram_delivery_service import (
    TelegramDeliveryService,
)
from presentation.telegram.telegram_send_result import (
    TelegramSendResult,
)


class FakeTelegramSender:
    def __init__(
        self,
        failures_by_text: dict[
            str,
            str,
        ] | None = None,
        exception: Exception | None = None,
    ) -> None:
        self._failures_by_text = (
            failures_by_text or {}
        )

        self._exception = exception

        self.calls: list[
            dict[str, Any]
        ] = []

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str | None = None,
        disable_web_page_preview: bool = True,
    ) -> TelegramSendResult:
        self.calls.append(
            {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": (
                    disable_web_page_preview
                ),
            }
        )

        if self._exception is not None:
            raise self._exception

        for marker, error in (
            self._failures_by_text.items()
        ):
            if marker in text:
                return TelegramSendResult(
                    success=False,
                    chat_id=chat_id,
                    message=None,
                    error=error,
                )

        return TelegramSendResult(
            success=True,
            chat_id=chat_id,
            message=(
                "Telegram message sent successfully"
            ),
            error=None,
        )


def create_success_client_result(
    client_id: str,
    report_text: str,
) -> DailyProductionClientResult:
    return DailyProductionClientResult(
        success=True,
        client_id=client_id,
        portfolio_file_path=(
            f"client_{client_id}.csv"
        ),
        report_text=report_text,
        error=None,
    )


def create_failed_client_result(
    client_id: str,
) -> DailyProductionClientResult:
    return DailyProductionClientResult(
        success=False,
        client_id=client_id,
        portfolio_file_path=None,
        report_text=None,
        error="portfolio analysis failed",
    )


def create_runner_result(
    *client_results: DailyProductionClientResult,
) -> DailyProductionRunnerResult:
    return DailyProductionRunnerResult(
        results=tuple(client_results),
        message="Daily production completed",
        error=None,
    )


def test_constructor_rejects_none_sender() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "telegram_sender must not be None"
        ),
    ):
        TelegramDeliveryService(
            telegram_sender=None
        )


def test_disabled_delivery_has_no_side_effect() -> None:
    sender = FakeTelegramSender()

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=False,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT ANH MANH",
        )
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.enabled is False
    assert result.succeeded is True
    assert result.total_count == 0

    assert (
        result.message
        == "Telegram delivery is disabled"
    )

    assert result.error is None
    assert sender.calls == []


def test_enabled_delivery_sends_successful_reports() -> None:
    sender = FakeTelegramSender()

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=True,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT ANH MANH",
        ),
        create_success_client_result(
            client_id="anh_thao",
            report_text="REPORT ANH THAO",
        ),
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.enabled is True
    assert result.succeeded is True

    assert result.total_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    assert len(sender.calls) == 2

    assert (
        sender.calls[0]["chat_id"]
        == "123456"
    )

    assert (
        "DMI REPORT — anh_manh"
        in sender.calls[0]["text"]
    )

    assert (
        "REPORT ANH MANH"
        in sender.calls[0]["text"]
    )

    assert (
        sender.calls[0]["parse_mode"]
        == "Markdown"
    )

    assert (
        sender.calls[0][
            "disable_web_page_preview"
        ]
        is True
    )


def test_failed_production_clients_are_not_sent() -> None:
    sender = FakeTelegramSender()

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=True,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT ANH MANH",
        ),
        create_failed_client_result(
            client_id="anh_dung"
        ),
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.total_count == 1
    assert result.success_count == 1

    assert len(sender.calls) == 1

    assert (
        "anh_manh"
        in sender.calls[0]["text"]
    )

    assert (
        "anh_dung"
        not in sender.calls[0]["text"]
    )


def test_send_failure_is_isolated() -> None:
    sender = FakeTelegramSender(
        failures_by_text={
            "anh_thao": "Telegram API error"
        }
    )

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=True,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT ANH MANH",
        ),
        create_success_client_result(
            client_id="anh_thao",
            report_text="REPORT ANH THAO",
        ),
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.succeeded is False
    assert result.partially_succeeded is True

    assert result.total_count == 2
    assert result.success_count == 1
    assert result.failure_count == 1

    failed_result = result.failed_results[0]

    assert (
        failed_result.client_id
        == "anh_thao"
    )

    assert (
        failed_result.error
        == "Telegram API error"
    )


def test_sender_exception_is_isolated_per_client() -> None:
    sender = FakeTelegramSender(
        exception=RuntimeError(
            "network unavailable"
        )
    )

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=True,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT ANH MANH",
        )
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.succeeded is False
    assert result.total_count == 1
    assert result.failure_count == 1

    assert (
        result.failed_results[0].error
        == "network unavailable"
    )


def test_no_successful_reports_is_valid() -> None:
    sender = FakeTelegramSender()

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=True,
    )

    production_result = create_runner_result(
        create_failed_client_result(
            client_id="anh_dung"
        )
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.enabled is True
    assert result.succeeded is True
    assert result.total_count == 0

    assert result.message == (
        "Telegram delivery completed: "
        "no successful client reports"
    )

    assert sender.calls == []


def test_deliver_rejects_none_production_result() -> None:
    service = TelegramDeliveryService(
        telegram_sender=FakeTelegramSender(),
        enabled=True,
    )

    with pytest.raises(
        ValueError,
        match=(
            "production_result must not be None"
        ),
    ):
        service.deliver(
            production_result=None,
            chat_id="123456",
        )


def test_deliver_rejects_empty_chat_id() -> None:
    service = TelegramDeliveryService(
        telegram_sender=FakeTelegramSender(),
        enabled=True,
    )

    with pytest.raises(
        ValueError,
        match="chat_id must not be empty",
    ):
        service.deliver(
            production_result=(
                create_runner_result()
            ),
            chat_id="   ",
        )


def test_invalid_sender_result_becomes_client_failure() -> None:
    class InvalidSender:
        def send_message(
            self,
            chat_id: str,
            text: str,
            parse_mode: str | None = None,
            disable_web_page_preview: bool = True,
        ) -> str:
            return "invalid result"

    service = TelegramDeliveryService(
        telegram_sender=InvalidSender(),
        enabled=True,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT",
        )
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.failure_count == 1

    assert result.failed_results[0].error == (
        "telegram_sender.send_message "
        "must return TelegramSendResult"
    )


def test_missing_send_method_becomes_client_failure() -> None:
    service = TelegramDeliveryService(
        telegram_sender=object(),
        enabled=True,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="REPORT",
        )
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.failure_count == 1

    assert result.failed_results[0].error == (
        "telegram_sender must have "
        "send_message method"
    )


def test_custom_parse_mode_is_forwarded() -> None:
    sender = FakeTelegramSender()

    service = TelegramDeliveryService(
        telegram_sender=sender,
        enabled=True,
        parse_mode="HTML",
        disable_web_page_preview=False,
    )

    production_result = create_runner_result(
        create_success_client_result(
            client_id="anh_manh",
            report_text="<b>REPORT</b>",
        )
    )

    result = service.deliver(
        production_result=production_result,
        chat_id="123456",
    )

    assert result.succeeded is True

    assert (
        sender.calls[0]["parse_mode"]
        == "HTML"
    )

    assert (
        sender.calls[0][
            "disable_web_page_preview"
        ]
        is False
    )