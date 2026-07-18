from presentation.telegram.telegram_sender import TelegramSender


def test_telegram_sender_requires_bot_token():
    try:
        TelegramSender("")
    except ValueError as exc:
        assert str(exc) == "bot_token must not be empty"
    else:
        assert False


def test_telegram_sender_requires_chat_id():
    sender = TelegramSender("fake-token")

    try:
        sender.send_message("", "hello")
    except ValueError as exc:
        assert str(exc) == "chat_id must not be empty"
    else:
        assert False


def test_telegram_sender_requires_text():
    sender = TelegramSender("fake-token")

    try:
        sender.send_message("123", "")
    except ValueError as exc:
        assert str(exc) == "text must not be empty"
    else:
        assert False


def test_telegram_sender_returns_success_when_api_ok():
    class FakeTelegramSender(TelegramSender):
        def _post(self, method, payload):
            assert method == "sendMessage"
            assert payload["chat_id"] == "123"
            assert payload["text"] == "hello"
            return {"ok": True, "result": {"message_id": 1}}

    sender = FakeTelegramSender("fake-token")

    result = sender.send_message("123", "hello")

    assert result.success is True
    assert result.chat_id == "123"
    assert result.message == "Telegram message sent successfully"
    assert result.error is None


def test_telegram_sender_returns_failed_when_api_not_ok():
    class FakeTelegramSender(TelegramSender):
        def _post(self, method, payload):
            return {"ok": False, "description": "Bad Request"}

    sender = FakeTelegramSender("fake-token")

    result = sender.send_message("123", "hello")

    assert result.success is False
    assert result.chat_id == "123"
    assert result.message is None
    assert "Bad Request" in result.error


def test_telegram_sender_returns_failed_when_exception():
    class FakeTelegramSender(TelegramSender):
        def _post(self, method, payload):
            raise RuntimeError("network error")

    sender = FakeTelegramSender("fake-token")

    result = sender.send_message("123", "hello")

    assert result.success is False
    assert result.chat_id == "123"
    assert result.message is None
    assert result.error == "network error"