from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramSendResult:
    success: bool
    chat_id: str
    message: str | None = None
    error: str | None = None