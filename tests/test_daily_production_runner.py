from __future__ import annotations

from pathlib import Path

import pytest

from apps.portfolio.services.daily_production_runner import (
    DailyProductionRunner,
)


class FakeClientRegistryRepository:
    def __init__(
        self,
        client_ids: list[str] | None = None,
        error: Exception | None = None,
    ) -> None:
        self._client_ids = (
            client_ids
            if client_ids is not None
            else []
        )

        self._error = error
        self.call_count = 0

    def load_client_ids(self) -> list[str]:
        self.call_count += 1

        if self._error is not None:
            raise self._error

        return list(self._client_ids)


class FakeClientPortfolioRepository:
    def __init__(
        self,
        folder: Path,
        existing_client_ids: set[str] | None = None,
    ) -> None:
        self._folder = folder

        self._existing_client_ids = (
            existing_client_ids
            if existing_client_ids is not None
            else set()
        )

        self.path_calls: list[str] = []
        self.exists_calls: list[str] = []

    def get_portfolio_path(
        self,
        client_id: str,
    ) -> str:
        self.path_calls.append(client_id)

        return str(
            self._folder
            / f"client_{client_id}.csv"
        )

    def exists(
        self,
        client_id: str,
    ) -> bool:
        self.exists_calls.append(client_id)

        return (
            client_id
            in self._existing_client_ids
        )


class FakeDailyPortfolioReportService:
    def __init__(
        self,
        reports: dict[str, str] | None = None,
        errors: dict[str, Exception] | None = None,
    ) -> None:
        self._reports = reports or {}
        self._errors = errors or {}
        self.calls: list[str] = []

    def generate(
        self,
        csv_file: str | Path,
    ) -> str:
        path = str(csv_file)
        self.calls.append(path)

        file_name = Path(path).name

        if file_name in self._errors:
            raise self._errors[file_name]

        return self._reports.get(
            file_name,
            "PORTFOLIO REPORT",
        )


def create_runner(
    tmp_path: Path,
    client_ids: list[str],
    existing_client_ids: set[str],
    reports: dict[str, str] | None = None,
    errors: dict[str, Exception] | None = None,
) -> tuple[
    DailyProductionRunner,
    FakeClientRegistryRepository,
    FakeClientPortfolioRepository,
    FakeDailyPortfolioReportService,
]:
    registry = FakeClientRegistryRepository(
        client_ids=client_ids
    )

    portfolio_repository = (
        FakeClientPortfolioRepository(
            folder=tmp_path,
            existing_client_ids=(
                existing_client_ids
            ),
        )
    )

    report_service = (
        FakeDailyPortfolioReportService(
            reports=reports,
            errors=errors,
        )
    )

    runner = DailyProductionRunner(
        client_registry_repository=registry,
        client_portfolio_repository=(
            portfolio_repository
        ),
        daily_portfolio_report_service=(
            report_service
        ),
    )

    return (
        runner,
        registry,
        portfolio_repository,
        report_service,
    )


def test_constructor_rejects_none_registry() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "client_registry_repository "
            "must not be None"
        ),
    ):
        DailyProductionRunner(
            client_registry_repository=None,
            client_portfolio_repository=object(),
            daily_portfolio_report_service=object(),
        )


def test_constructor_rejects_none_portfolio_repository() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "client_portfolio_repository "
            "must not be None"
        ),
    ):
        DailyProductionRunner(
            client_registry_repository=object(),
            client_portfolio_repository=None,
            daily_portfolio_report_service=object(),
        )


def test_constructor_rejects_none_report_service() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "daily_portfolio_report_service "
            "must not be None"
        ),
    ):
        DailyProductionRunner(
            client_registry_repository=object(),
            client_portfolio_repository=object(),
            daily_portfolio_report_service=None,
        )


def test_run_all_clients_successfully(
    tmp_path: Path,
) -> None:
    runner, registry, repository, report_service = (
        create_runner(
            tmp_path=tmp_path,
            client_ids=[
                "anh_dung",
                "chi_lan",
            ],
            existing_client_ids={
                "anh_dung",
                "chi_lan",
            },
            reports={
                "client_anh_dung.csv": (
                    "REPORT ANH DUNG"
                ),
                "client_chi_lan.csv": (
                    "REPORT CHI LAN"
                ),
            },
        )
    )

    result = runner.run()

    assert result.succeeded is True
    assert result.failed is False
    assert result.partially_succeeded is False

    assert result.total_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    assert result.reports_by_client == {
        "anh_dung": "REPORT ANH DUNG",
        "chi_lan": "REPORT CHI LAN",
    }

    assert result.message == (
        "Daily production completed: "
        "2 succeeded, 0 failed"
    )

    assert result.error is None
    assert registry.call_count == 1

    assert repository.exists_calls == [
        "anh_dung",
        "chi_lan",
    ]

    assert len(report_service.calls) == 2


def test_run_continues_when_one_client_fails(
    tmp_path: Path,
) -> None:
    runner, _, _, report_service = create_runner(
        tmp_path=tmp_path,
        client_ids=[
            "anh_dung",
            "chi_lan",
        ],
        existing_client_ids={
            "anh_dung",
            "chi_lan",
        },
        reports={
            "client_anh_dung.csv": (
                "REPORT ANH DUNG"
            ),
        },
        errors={
            "client_chi_lan.csv": RuntimeError(
                "analysis failed"
            ),
        },
    )

    result = runner.run()

    assert result.succeeded is False
    assert result.partially_succeeded is True
    assert result.failed is True

    assert result.total_count == 2
    assert result.success_count == 1
    assert result.failure_count == 1

    anh_dung_result = (
        result.get_result_by_client_id(
            "anh_dung"
        )
    )

    chi_lan_result = (
        result.get_result_by_client_id(
            "chi_lan"
        )
    )

    assert anh_dung_result is not None
    assert anh_dung_result.success is True

    assert chi_lan_result is not None
    assert chi_lan_result.success is False
    assert chi_lan_result.error == "analysis failed"

    assert len(report_service.calls) == 2


def test_missing_portfolio_file_is_client_failure(
    tmp_path: Path,
) -> None:
    runner, _, _, report_service = create_runner(
        tmp_path=tmp_path,
        client_ids=["anh_dung"],
        existing_client_ids=set(),
    )

    result = runner.run()

    assert result.total_count == 1
    assert result.success_count == 0
    assert result.failure_count == 1
    assert result.failed is True

    client_result = result.results[0]

    assert client_result.success is False
    assert client_result.client_id == "anh_dung"
    assert client_result.error is not None
    assert "portfolio file not found" in (
        client_result.error
    )

    assert report_service.calls == []


def test_registry_failure_becomes_runner_error(
    tmp_path: Path,
) -> None:
    registry = FakeClientRegistryRepository(
        error=RuntimeError(
            "client registry unavailable"
        )
    )

    repository = FakeClientPortfolioRepository(
        folder=tmp_path
    )

    report_service = (
        FakeDailyPortfolioReportService()
    )

    runner = DailyProductionRunner(
        client_registry_repository=registry,
        client_portfolio_repository=repository,
        daily_portfolio_report_service=(
            report_service
        ),
    )

    result = runner.run()

    assert result.results == ()
    assert result.total_count == 0
    assert result.success_count == 0
    assert result.failure_count == 0

    assert result.succeeded is False
    assert result.failed is True

    assert (
        result.error
        == "client registry unavailable"
    )

    assert result.message is None
    assert report_service.calls == []


def test_empty_registry_is_valid(
    tmp_path: Path,
) -> None:
    runner, _, _, report_service = create_runner(
        tmp_path=tmp_path,
        client_ids=[],
        existing_client_ids=set(),
    )

    result = runner.run()

    assert result.succeeded is True
    assert result.total_count == 0
    assert result.success_count == 0
    assert result.failure_count == 0

    assert result.message == (
        "Daily production completed: "
        "no clients found"
    )

    assert result.error is None
    assert report_service.calls == []


def test_duplicate_client_ids_are_processed_once(
    tmp_path: Path,
) -> None:
    runner, _, repository, report_service = (
        create_runner(
            tmp_path=tmp_path,
            client_ids=[
                "anh_dung",
                "anh_dung",
                "chi_lan",
            ],
            existing_client_ids={
                "anh_dung",
                "chi_lan",
            },
        )
    )

    result = runner.run()

    assert result.total_count == 2
    assert result.success_count == 2

    assert repository.exists_calls == [
        "anh_dung",
        "chi_lan",
    ]

    assert len(report_service.calls) == 2


def test_run_client_successfully(
    tmp_path: Path,
) -> None:
    runner, registry, _, report_service = (
        create_runner(
            tmp_path=tmp_path,
            client_ids=[],
            existing_client_ids={
                "anh_dung"
            },
            reports={
                "client_anh_dung.csv": (
                    "REPORT ANH DUNG"
                )
            },
        )
    )

    result = runner.run_client("anh_dung")

    assert result.success is True
    assert result.client_id == "anh_dung"
    assert result.report_text == "REPORT ANH DUNG"
    assert result.error is None

    assert registry.call_count == 0
    assert len(report_service.calls) == 1


def test_run_client_rejects_empty_client_id(
    tmp_path: Path,
) -> None:
    runner, _, _, _ = create_runner(
        tmp_path=tmp_path,
        client_ids=[],
        existing_client_ids=set(),
    )

    with pytest.raises(
        ValueError,
        match="client_id must not be empty",
    ):
        runner.run_client("   ")


def test_empty_report_is_client_failure(
    tmp_path: Path,
) -> None:
    runner, _, _, _ = create_runner(
        tmp_path=tmp_path,
        client_ids=["anh_dung"],
        existing_client_ids={"anh_dung"},
        reports={
            "client_anh_dung.csv": "   "
        },
    )

    result = runner.run()

    assert result.total_count == 1
    assert result.success_count == 0
    assert result.failure_count == 1

    client_result = result.results[0]

    assert client_result.success is False
    assert client_result.error is not None

    assert "returned empty report" in (
        client_result.error
    )