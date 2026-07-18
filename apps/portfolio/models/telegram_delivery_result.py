from __future__ import annotations

from dataclasses import dataclass, field

from apps.portfolio.models.telegram_delivery_item_result import (
    TelegramDeliveryItemResult,
)


@dataclass(frozen=True, slots=True)
class TelegramDeliveryResult:
    """
    Kết quả tổng hợp của một lần Telegram Delivery.

    Telegram Delivery là kênh thông báo phụ.

    Việc delivery thất bại không làm thay đổi
    DailyProductionRunnerResult và không quyết định
    exit code của pipeline phân tích.
    """

    enabled: bool

    results: tuple[
        TelegramDeliveryItemResult,
        ...,
    ] = field(default_factory=tuple)

    message: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        normalized_results = tuple(self.results)

        for result in normalized_results:
            if not isinstance(
                result,
                TelegramDeliveryItemResult,
            ):
                raise TypeError(
                    "results must contain only "
                    "TelegramDeliveryItemResult"
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
        if not self.enabled:
            return True

        return (
            self.error is None
            and self.failure_count == 0
        )

    @property
    def partially_succeeded(self) -> bool:
        return (
            self.enabled
            and self.success_count > 0
            and self.failure_count > 0
        )

    @property
    def failed(self) -> bool:
        return not self.succeeded

    @property
    def successful_results(
        self,
    ) -> tuple[
        TelegramDeliveryItemResult,
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
        TelegramDeliveryItemResult,
        ...,
    ]:
        return tuple(
            result
            for result in self.results
            if not result.success
        )

    def _normalize_optional_text(
        self,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()

        return normalized or None