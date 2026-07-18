from apps.portfolio.application.portfolio_daily_application import (
    PortfolioDailyApplication,
)


class FakeDailyReportService:
    def run(self, client_id: str):
        return {
            "client_id": client_id,
            "value": f"report:{client_id}",
        }


class FakeRenderer:
    def render(self, report):
        return f"rendered:{report['client_id']}"


class FakeTelegramSender:
    def __init__(self):
        self.sent_messages = []

    def send_message(self, chat_id: str, text: str):
        result = {
            "chat_id": chat_id,
            "text": text,
            "success": True,
        }
        self.sent_messages.append(result)
        return result


def test_portfolio_daily_application_requires_daily_report_service():
    try:
        PortfolioDailyApplication(
            daily_report_service=None,
            renderer=FakeRenderer(),
        )
    except ValueError as exc:
        assert str(exc) == "daily_report_service must not be None"
    else:
        assert False


def test_portfolio_daily_application_requires_renderer():
    try:
        PortfolioDailyApplication(
            daily_report_service=FakeDailyReportService(),
            renderer=None,
        )
    except ValueError as exc:
        assert str(exc) == "renderer must not be None"
    else:
        assert False


def test_portfolio_daily_application_rejects_none_client_ids():
    app = PortfolioDailyApplication(
        daily_report_service=FakeDailyReportService(),
        renderer=FakeRenderer(),
    )

    try:
        app.run(None)
    except ValueError as exc:
        assert str(exc) == "client_ids must not be None"
    else:
        assert False


def test_portfolio_daily_application_runs_for_all_clients_without_telegram():
    app = PortfolioDailyApplication(
        daily_report_service=FakeDailyReportService(),
        renderer=FakeRenderer(),
    )

    result = app.run(["client_a", "client_b"])

    assert result.success is True
    assert result.total_clients == 2
    assert result.success_count == 2
    assert result.failed_count == 0
    assert result.has_failed is False
    assert result.error is None

    batch_result = result.data
    assert batch_result.results[0].success is True
    assert batch_result.results[0].data["client_id"] == "client_a"
    assert batch_result.results[0].data["rendered_text"] == "rendered:client_a"
    assert batch_result.results[0].data["telegram_result"] is None


def test_portfolio_daily_application_runs_for_all_clients_with_telegram():
    telegram_sender = FakeTelegramSender()

    app = PortfolioDailyApplication(
        daily_report_service=FakeDailyReportService(),
        renderer=FakeRenderer(),
        telegram_sender=telegram_sender,
        chat_id="123",
    )

    result = app.run(["client_a", "client_b"])

    assert result.success is True
    assert result.total_clients == 2
    assert result.success_count == 2
    assert result.failed_count == 0

    assert len(telegram_sender.sent_messages) == 2
    assert telegram_sender.sent_messages[0]["chat_id"] == "123"
    assert telegram_sender.sent_messages[0]["text"] == "rendered:client_a"
    assert telegram_sender.sent_messages[1]["text"] == "rendered:client_b"


def test_portfolio_daily_application_requires_chat_id_when_telegram_enabled():
    telegram_sender = FakeTelegramSender()

    app = PortfolioDailyApplication(
        daily_report_service=FakeDailyReportService(),
        renderer=FakeRenderer(),
        telegram_sender=telegram_sender,
        chat_id="",
    )

    result = app.run(["client_a"])

    assert result.success is False
    assert result.total_clients == 1
    assert result.success_count == 0
    assert result.failed_count == 1
    assert result.error == "some clients failed"

    failed = result.data.results[0]
    assert failed.success is False
    assert failed.error == "chat_id must not be empty when telegram_sender is provided"


def test_portfolio_daily_application_continues_when_one_client_fails():
    class FailingDailyReportService:
        def run(self, client_id: str):
            if client_id == "bad_client":
                raise RuntimeError("report failed")
            return {"client_id": client_id}

    app = PortfolioDailyApplication(
        daily_report_service=FailingDailyReportService(),
        renderer=FakeRenderer(),
    )

    result = app.run(["client_a", "bad_client", "client_b"])

    assert result.success is False
    assert result.total_clients == 3
    assert result.success_count == 2
    assert result.failed_count == 1
    assert result.has_failed is True
    assert result.error == "some clients failed"

    assert result.data.results[0].success is True
    assert result.data.results[1].success is False
    assert result.data.results[1].error == "report failed"
    assert result.data.results[2].success is True


def test_portfolio_daily_application_supports_execute_method():
    class ExecuteDailyReportService:
        def execute(self, client_id: str):
            return {"client_id": client_id}

    app = PortfolioDailyApplication(
        daily_report_service=ExecuteDailyReportService(),
        renderer=FakeRenderer(),
    )

    result = app.run(["client_a"])

    assert result.success is True
    assert result.success_count == 1


def test_portfolio_daily_application_supports_generate_method():
    class GenerateDailyReportService:
        def generate(self, client_id: str):
            return {"client_id": client_id}

    app = PortfolioDailyApplication(
        daily_report_service=GenerateDailyReportService(),
        renderer=FakeRenderer(),
    )

    result = app.run(["client_a"])

    assert result.success is True
    assert result.success_count == 1


def test_portfolio_daily_application_requires_service_method():
    class InvalidDailyReportService:
        pass

    app = PortfolioDailyApplication(
        daily_report_service=InvalidDailyReportService(),
        renderer=FakeRenderer(),
    )

    result = app.run(["client_a"])

    assert result.success is False
    assert result.failed_count == 1
    assert (
        result.data.results[0].error
        == "daily_report_service must have run, execute, or generate method"
    )


def test_portfolio_daily_application_requires_renderer_render_method():
    class InvalidRenderer:
        pass

    app = PortfolioDailyApplication(
        daily_report_service=FakeDailyReportService(),
        renderer=InvalidRenderer(),
    )

    result = app.run(["client_a"])

    assert result.success is False
    assert result.failed_count == 1
    assert result.data.results[0].error == "renderer must have render method"


def test_portfolio_daily_application_requires_telegram_send_message_method():
    class InvalidTelegramSender:
        pass

    app = PortfolioDailyApplication(
        daily_report_service=FakeDailyReportService(),
        renderer=FakeRenderer(),
        telegram_sender=InvalidTelegramSender(),
        chat_id="123",
    )

    result = app.run(["client_a"])

    assert result.success is False
    assert result.failed_count == 1
    assert result.data.results[0].error == "telegram_sender must have send_message method"