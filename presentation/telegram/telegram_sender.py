import json
import urllib.parse
import urllib.request
from typing import Any

from presentation.telegram.telegram_send_result import TelegramSendResult


class TelegramSender:
    """
    Send text message to Telegram.

    Responsibility:
    - gửi message đã render sẵn lên Telegram
    - không build report
    - không render markdown
    - không đọc portfolio
    - không orchestration business flow
    """

    def __init__(self, bot_token: str, timeout: int = 10):
        if bot_token is None or not str(bot_token).strip():
            raise ValueError("bot_token must not be empty")

        self._bot_token = str(bot_token).strip()
        self._timeout = timeout

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str | None = None,
        disable_web_page_preview: bool = True,
    ) -> TelegramSendResult:
        if chat_id is None or not str(chat_id).strip():
            raise ValueError("chat_id must not be empty")

        if text is None or not str(text).strip():
            raise ValueError("text must not be empty")

        normalized_chat_id = str(chat_id).strip()
        normalized_text = str(text)

        payload: dict[str, Any] = {
            "chat_id": normalized_chat_id,
            "text": normalized_text,
            "disable_web_page_preview": disable_web_page_preview,
        }

        if parse_mode is not None and str(parse_mode).strip():
            payload["parse_mode"] = str(parse_mode).strip()

        try:
            response = self._post("sendMessage", payload)

            if response.get("ok") is True:
                return TelegramSendResult(
                    success=True,
                    chat_id=normalized_chat_id,
                    message="Telegram message sent successfully",
                    error=None,
                )

            return TelegramSendResult(
                success=False,
                chat_id=normalized_chat_id,
                message=None,
                error=str(response),
            )

        except Exception as exc:
            return TelegramSendResult(
                success=False,
                chat_id=normalized_chat_id,
                message=None,
                error=str(exc),
            )

    def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/{method}"

        encoded_payload = urllib.parse.urlencode(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=encoded_payload,
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            raw_body = response.read().decode("utf-8")

        return json.loads(raw_body)