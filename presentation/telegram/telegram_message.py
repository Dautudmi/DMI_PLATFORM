from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelegramMessage:
    """
    Message DTO dành cho Telegram presentation layer.

    Responsibility:
    - lưu nội dung cần gửi
    - lưu parse mode
    - hỗ trợ ghép title và body thành text hoàn chỉnh

    Không:
    - gửi HTTP request
    - biết bot token
    - biết chat ID
    - chứa business logic
    """

    body: str
    title: str | None = None
    parse_mode: str | None = "Markdown"

    def __post_init__(self) -> None:
        normalized_body = self._normalize_required_text(
            value=self.body,
            field_name="body",
        )

        normalized_title = self._normalize_optional_text(
            self.title
        )

        normalized_parse_mode = (
            self._normalize_optional_text(
                self.parse_mode
            )
        )

        object.__setattr__(
            self,
            "body",
            normalized_body,
        )

        object.__setattr__(
            self,
            "title",
            normalized_title,
        )

        object.__setattr__(
            self,
            "parse_mode",
            normalized_parse_mode,
        )

    @property
    def text(self) -> str:
        if self.title is None:
            return self.body

        return "\n\n".join(
            [
                self.title,
                self.body,
            ]
        )

    @property
    def is_markdown(self) -> bool:
        if self.parse_mode is None:
            return False

        return self.parse_mode.lower() in {
            "markdown",
            "markdownv2",
        }

    @property
    def is_html(self) -> bool:
        if self.parse_mode is None:
            return False

        return self.parse_mode.lower() == "html"

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