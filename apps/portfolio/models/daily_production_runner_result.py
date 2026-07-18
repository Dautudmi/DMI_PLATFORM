from __future__ import annotations

from dataclasses import dataclass, field

from apps.portfolio.models.daily_production_client_result import (
    DailyProductionClientResult,
)


@dataclass(frozen=True, slots=True)
class DailyProductionRunnerResult:
    """
    Kết quả tổng hợp của DailyProductionRunner.

    Responsibility:
    - lưu kết quả của từng khách hàng
    - tổng hợp số lượng thành công
    - tổng hợp số lượng thất bại
    - thể hiện lỗi cấp Runner

    Không:
    - load Client Registry
    - load Portfolio
    - tạo báo cáo
    - gửi Telegram
    """

    results: tuple[
        DailyProductionClientResult,
        ...,
    ] = field(default_factory=tuple)

    message: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        normalized_results = tuple(self.results)

        for result in normalized_results:
            if not isinstance(
                result,
                DailyProductionClientResult,
            ):
                raise TypeError(
                    "results must contain only "
                    "DailyProductionClientResult"
                )

        normalized_message = self._normalize_optional_text(
            self.message
        )

        normalized_error = self._normalize_optional_text(
            self.error
        )

        object.__setattr__(
            self,
            "results",
            normalized_results,
        )

        object.__setattr__(
            self,
            "message",
            normalized_message,
        )

        object.__setattr__(
            self,
            "error",
            normalized_error,
        )

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(
            1
            for result in self.results
            if result.success
        )

    @property
    def failure_count(self) -> int:
        return self.total_count - self.success_count

    @property
    def succeeded(self) -> bool:
        return (
            self.error is None
            and self.failure_count == 0
        )

    @property
    def partially_succeeded(self) -> bool:
        return (
            self.success_count > 0
            and self.failure_count > 0
        )

    @property
    def failed(self) -> bool:
        return not self.succeeded

    @property
    def successful_results(
        self,
    ) -> tuple[
        DailyProductionClientResult,
        ...,
    ]:
        return tuple(
            result
            for result in self.results
            if result.success
        )

    @property
    def failed_results(
        self,
    ) -> tuple[
        DailyProductionClientResult,
        ...,
    ]:
        return tuple(
            result
            for result in self.results
            if not result.success
        )

    @property
    def reports_by_client(
        self,
    ) -> dict[str, str]:
        reports: dict[str, str] = {}

        for result in self.successful_results:
            if result.report_text is not None:
                reports[result.client_id] = (
                    result.report_text
                )

        return reports

    def get_result_by_client_id(
        self,
        client_id: str,
    ) -> DailyProductionClientResult | None:
        normalized_client_id = (
            self._normalize_required_text(
                value=client_id,
                field_name="client_id",
            )
        )

        for result in self.results:
            if result.client_id == normalized_client_id:
                return result

        return None

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