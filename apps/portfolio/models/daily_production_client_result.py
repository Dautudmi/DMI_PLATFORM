from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DailyProductionClientResult:
    """
    Kết quả Daily Production của một khách hàng.

    Responsibility:
    - lưu client_id
    - lưu đường dẫn file danh mục
    - lưu nội dung report đã render
    - lưu trạng thái thành công hoặc thất bại

    Không:
    - đọc Client Registry
    - đọc Portfolio CSV
    - phân tích Portfolio
    - render báo cáo
    - gửi Telegram
    """

    success: bool
    client_id: str

    portfolio_file_path: str | None = None
    report_text: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        normalized_client_id = self._normalize_required_text(
            value=self.client_id,
            field_name="client_id",
        )

        normalized_portfolio_file_path = (
            self._normalize_optional_text(
                self.portfolio_file_path
            )
        )

        normalized_report_text = (
            self._normalize_optional_text(
                self.report_text
            )
        )

        normalized_error = self._normalize_optional_text(
            self.error
        )

        if self.success:
            if normalized_portfolio_file_path is None:
                raise ValueError(
                    "portfolio_file_path is required "
                    "when success is True"
                )

            if normalized_report_text is None:
                raise ValueError(
                    "report_text is required "
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
            "portfolio_file_path",
            normalized_portfolio_file_path,
        )

        object.__setattr__(
            self,
            "report_text",
            normalized_report_text,
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