from __future__ import annotations

from typing import Any

from apps.portfolio.models.daily_production_client_result import (
    DailyProductionClientResult,
)
from apps.portfolio.models.daily_production_runner_result import (
    DailyProductionRunnerResult,
)


class DailyProductionRunner:
    """
    Application Service điều phối Daily Production
    cho toàn bộ khách hàng PE_V2.4.

    Flow:

    Client Registry Repository
        ↓
    load_client_ids()
        ↓
    Client Portfolio Repository
        ↓
    get_portfolio_path(client_id)
        ↓
    DailyPortfolioReportService
        ↓
    Telegram-ready report text
        ↓
    DailyProductionRunnerResult

    Responsibility:
    - lấy danh sách client_id
    - xác định file danh mục từng khách
    - kiểm tra file danh mục tồn tại
    - gọi DailyPortfolioReportService
    - cô lập lỗi của từng khách
    - tổng hợp kết quả

    Không:
    - tạo Transaction
    - áp dụng PositionEngine
    - ghi Trade History
    - ghi Portfolio
    - gửi Telegram
    - chạy Scheduler
    """

    def __init__(
        self,
        client_registry_repository: Any,
        client_portfolio_repository: Any,
        daily_portfolio_report_service: Any,
    ) -> None:
        if client_registry_repository is None:
            raise ValueError(
                "client_registry_repository must not be None"
            )

        if client_portfolio_repository is None:
            raise ValueError(
                "client_portfolio_repository must not be None"
            )

        if daily_portfolio_report_service is None:
            raise ValueError(
                "daily_portfolio_report_service must not be None"
            )

        self._client_registry_repository = (
            client_registry_repository
        )

        self._client_portfolio_repository = (
            client_portfolio_repository
        )

        self._daily_portfolio_report_service = (
            daily_portfolio_report_service
        )

    def run(self) -> DailyProductionRunnerResult:
        """
        Chạy Daily Production cho toàn bộ khách hàng.

        Lỗi khi đọc Client Registry là lỗi cấp Runner.

        Lỗi của một khách hàng được ghi vào
        DailyProductionClientResult và không làm dừng
        các khách hàng còn lại.
        """

        try:
            client_ids = self._load_client_ids()

        except Exception as exc:
            return DailyProductionRunnerResult(
                results=(),
                message=None,
                error=str(exc),
            )

        results: list[
            DailyProductionClientResult
        ] = []

        for client_id in client_ids:
            result = self._run_client_safely(
                client_id=client_id
            )

            results.append(result)

        normalized_results = tuple(results)

        if not normalized_results:
            return DailyProductionRunnerResult(
                results=(),
                message=(
                    "Daily production completed: "
                    "no clients found"
                ),
                error=None,
            )

        success_count = sum(
            1
            for result in normalized_results
            if result.success
        )

        failure_count = (
            len(normalized_results) - success_count
        )

        return DailyProductionRunnerResult(
            results=normalized_results,
            message=(
                "Daily production completed: "
                f"{success_count} succeeded, "
                f"{failure_count} failed"
            ),
            error=None,
        )

    def run_client(
        self,
        client_id: str,
    ) -> DailyProductionClientResult:
        """
        Chạy Daily Production cho một khách hàng.

        Method này hữu ích cho:
        - chạy thử
        - debug
        - chạy thủ công một khách
        - CLI client-specific trong Sprint sau
        """

        normalized_client_id = (
            self._normalize_client_id(client_id)
        )

        return self._run_client_safely(
            client_id=normalized_client_id
        )

    def _run_client_safely(
        self,
        client_id: str,
    ) -> DailyProductionClientResult:
        try:
            normalized_client_id = (
                self._normalize_client_id(client_id)
            )

            portfolio_file_path = (
                self._get_portfolio_path(
                    normalized_client_id
                )
            )

            if not self._portfolio_exists(
                normalized_client_id
            ):
                return DailyProductionClientResult(
                    success=False,
                    client_id=normalized_client_id,
                    portfolio_file_path=(
                        portfolio_file_path
                    ),
                    report_text=None,
                    error=(
                        "portfolio file not found: "
                        f"{portfolio_file_path}"
                    ),
                )

            report_text = self._generate_report(
                portfolio_file_path
            )

            normalized_report_text = (
                self._normalize_report_text(
                    report_text
                )
            )

            return DailyProductionClientResult(
                success=True,
                client_id=normalized_client_id,
                portfolio_file_path=(
                    portfolio_file_path
                ),
                report_text=normalized_report_text,
                error=None,
            )

        except Exception as exc:
            return DailyProductionClientResult(
                success=False,
                client_id=(
                    str(client_id).strip()
                    if client_id is not None
                    and str(client_id).strip()
                    else "UNKNOWN"
                ),
                portfolio_file_path=None,
                report_text=None,
                error=str(exc),
            )

    def _load_client_ids(self) -> list[str]:
        repository = self._client_registry_repository

        if not hasattr(repository, "load_client_ids"):
            raise AttributeError(
                "client_registry_repository must have "
                "load_client_ids method"
            )

        client_ids = repository.load_client_ids()

        if client_ids is None:
            raise ValueError(
                "client registry returned None"
            )

        normalized_client_ids: list[str] = []
        seen_client_ids: set[str] = set()

        for client_id in client_ids:
            normalized_client_id = (
                self._normalize_client_id(client_id)
            )

            if normalized_client_id in seen_client_ids:
                continue

            normalized_client_ids.append(
                normalized_client_id
            )

            seen_client_ids.add(
                normalized_client_id
            )

        return normalized_client_ids

    def _get_portfolio_path(
        self,
        client_id: str,
    ) -> str:
        repository = self._client_portfolio_repository

        if not hasattr(repository, "get_portfolio_path"):
            raise AttributeError(
                "client_portfolio_repository must have "
                "get_portfolio_path method"
            )

        portfolio_file_path = (
            repository.get_portfolio_path(client_id)
        )

        if (
            portfolio_file_path is None
            or not str(portfolio_file_path).strip()
        ):
            raise ValueError(
                "client portfolio repository returned "
                "empty portfolio path"
            )

        return str(portfolio_file_path).strip()

    def _portfolio_exists(
        self,
        client_id: str,
    ) -> bool:
        repository = self._client_portfolio_repository

        if not hasattr(repository, "exists"):
            raise AttributeError(
                "client_portfolio_repository must have "
                "exists method"
            )

        return bool(repository.exists(client_id))

    def _generate_report(
        self,
        portfolio_file_path: str,
    ) -> str:
        service = self._daily_portfolio_report_service

        if not hasattr(service, "generate"):
            raise AttributeError(
                "daily_portfolio_report_service must have "
                "generate method"
            )

        return service.generate(
            portfolio_file_path
        )

    def _normalize_client_id(
        self,
        client_id: str,
    ) -> str:
        if client_id is None or not str(client_id).strip():
            raise ValueError(
                "client_id must not be empty"
            )

        return str(client_id).strip()

    def _normalize_report_text(
        self,
        report_text: str,
    ) -> str:
        if (
            report_text is None
            or not str(report_text).strip()
        ):
            raise ValueError(
                "daily portfolio report service "
                "returned empty report"
            )

        return str(report_text).strip()