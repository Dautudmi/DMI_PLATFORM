from typing import Iterable, Any

from apps.portfolio.application.portfolio_application_result import (
    PortfolioApplicationResult,
)
from apps.portfolio.services.client_batch_processor import ClientBatchProcessor


class PortfolioDailyApplication:
    """
    Portfolio Daily Application.

    Responsibility:
    - nhận danh sách client_id
    - chạy DailyPortfolioReportService cho từng client
    - render report
    - gửi Telegram nếu có telegram_sender
    - trả về kết quả tổng hợp

    Đây là Application Layer.
    Được phép orchestration.
    Không chứa business logic portfolio.
    Không tự đọc file.
    Không tự tính khuyến nghị.
    """

    def __init__(
        self,
        daily_report_service: Any,
        renderer: Any,
        telegram_sender: Any | None = None,
        chat_id: str | None = None,
    ):
        if daily_report_service is None:
            raise ValueError("daily_report_service must not be None")

        if renderer is None:
            raise ValueError("renderer must not be None")

        self._daily_report_service = daily_report_service
        self._renderer = renderer
        self._telegram_sender = telegram_sender
        self._chat_id = chat_id

    def run(self, client_ids: Iterable[str]) -> PortfolioApplicationResult:
        if client_ids is None:
            raise ValueError("client_ids must not be None")

        processor = ClientBatchProcessor(self._process_one_client)
        batch_result = processor.process(client_ids)

        return PortfolioApplicationResult(
            success=batch_result.is_success,
            total_clients=batch_result.total_clients,
            success_count=batch_result.success_count,
            failed_count=batch_result.failed_count,
            data=batch_result,
            error=None if batch_result.is_success else "some clients failed",
        )

    def _process_one_client(self, client_id: str) -> dict[str, Any]:
        report = self._build_report(client_id)
        rendered_text = self._render_report(report)
        telegram_result = self._send_telegram_if_enabled(rendered_text)

        return {
            "client_id": client_id,
            "report": report,
            "rendered_text": rendered_text,
            "telegram_result": telegram_result,
        }

    def _build_report(self, client_id: str) -> Any:
        if hasattr(self._daily_report_service, "run"):
            return self._daily_report_service.run(client_id)

        if hasattr(self._daily_report_service, "execute"):
            return self._daily_report_service.execute(client_id)

        if hasattr(self._daily_report_service, "generate"):
            return self._daily_report_service.generate(client_id)

        raise AttributeError(
            "daily_report_service must have run, execute, or generate method"
        )

    def _render_report(self, report: Any) -> str:
        if hasattr(self._renderer, "render"):
            return self._renderer.render(report)

        raise AttributeError("renderer must have render method")

    def _send_telegram_if_enabled(self, text: str) -> Any | None:
        if self._telegram_sender is None:
            return None

        if self._chat_id is None or not str(self._chat_id).strip():
            raise ValueError("chat_id must not be empty when telegram_sender is provided")

        if hasattr(self._telegram_sender, "send_message"):
            return self._telegram_sender.send_message(
                chat_id=str(self._chat_id).strip(),
                text=text,
            )

        raise AttributeError("telegram_sender must have send_message method")