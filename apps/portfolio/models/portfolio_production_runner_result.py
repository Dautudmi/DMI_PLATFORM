from __future__ import annotations

from dataclasses import dataclass, field

from apps.portfolio.models.portfolio_production_flow_result import (
    PortfolioProductionFlowResult,
)


@dataclass(frozen=True, slots=True)
class PortfolioProductionRunnerResult:
    """
    Kết quả tổng hợp của Portfolio Production Runner.

    Runner có thể xử lý nhiều Production Flow trong một lần chạy.

    Responsibility:
    - lưu danh sách kết quả từng flow
    - cung cấp số lượng thành công
    - cung cấp số lượng thất bại
    - cung cấp trạng thái tổng thể
    - cung cấp lỗi cấp Runner nếu có

    Không:
    - load Client Registry
    - thực thi Transaction
    - ghi Portfolio
    - ghi Trade History
    - tạo báo cáo
    - gửi Telegram
    """

    results: tuple[
        PortfolioProductionFlowResult,
        ...,
    ] = field(default_factory=tuple)

    message: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        normalized_results = tuple(self.results)

        for result in normalized_results:
            if not isinstance(
                result,
                PortfolioProductionFlowResult,
            ):
                raise TypeError(
                    "results must contain only "
                    "PortfolioProductionFlowResult"
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
        PortfolioProductionFlowResult,
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
        PortfolioProductionFlowResult,
        ...,
    ]:
        return tuple(
            result
            for result in self.results
            if not result.success
        )

    def get_result_by_client_name(
        self,
        client_name: str,
    ) -> PortfolioProductionFlowResult | None:
        normalized_client_name = self._normalize_required_text(
            value=client_name,
            field_name="client_name",
        )

        for result in self.results:
            portfolio = result.portfolio

            if portfolio is None:
                continue

            if (
                str(portfolio.client_name).strip()
                == normalized_client_name
            ):
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