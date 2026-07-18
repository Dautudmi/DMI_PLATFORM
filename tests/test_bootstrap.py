from __future__ import annotations

from pathlib import Path

import pytest

from apps.bootstrap import (
    PEV24_CLIENT_CONFIG_PATH_KEY,
    PEV24_CLIENTS_FOLDER_PATH_KEY,
    build_application,
)
from apps.portfolio.services.daily_production_runner import (
    DailyProductionRunner,
)
from apps.shared.containers.application import (
    ApplicationContainer,
)
from infrastructure.configuration import (
    Configuration,
    ConfigurationError,
)
from infrastructure.pe_v24.client_portfolio_repository import (
    PEV24ClientPortfolioRepository,
)
from infrastructure.pe_v24.client_registry_repository import (
    PEV24ClientRegistryRepository,
)


class FakeDailyPortfolioReportService:
    def __init__(
        self,
        report_text: str = "DMI REPORT",
    ) -> None:
        self._report_text = report_text
        self.calls: list[str] = []

    def generate(
        self,
        csv_file: str | Path,
    ) -> str:
        normalized_path = str(csv_file)

        self.calls.append(normalized_path)

        return self._report_text


def create_configuration(
    client_config_path: Path,
    clients_folder_path: Path,
) -> Configuration:
    return Configuration(
        values={
            PEV24_CLIENT_CONFIG_PATH_KEY: str(
                client_config_path
            ),
            PEV24_CLIENTS_FOLDER_PATH_KEY: str(
                clients_folder_path
            ),
        }
    )


def create_valid_production_paths(
    tmp_path: Path,
) -> tuple[Path, Path]:
    """
    Tạo cấu trúc production tối thiểu hợp lệ:

    tmp_path/
        client_config.csv
        clients/
    """

    client_config_path = (
        tmp_path / "client_config.csv"
    )

    clients_folder_path = (
        tmp_path / "clients"
    )

    client_config_path.write_text(
        "Client,Capital,CashPercent\n",
        encoding="utf-8-sig",
    )

    clients_folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        client_config_path,
        clients_folder_path,
    )


def write_client_config(
    file_path: Path,
    rows: list[str],
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    content = "\n".join(
        [
            "Client,Capital,CashPercent",
            *rows,
        ]
    )

    file_path.write_text(
        content,
        encoding="utf-8-sig",
    )


def write_client_portfolio(
    folder: Path,
    client_id: str,
) -> Path:
    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = (
        folder / f"client_{client_id}.csv"
    )

    file_path.write_text(
        "\n".join(
            [
                "Ticker,Quantity,AverageCost",
                "NAB,1200,12.45",
                "FTS,400,26.465",
            ]
        ),
        encoding="utf-8-sig",
    )

    return file_path


def test_build_application_returns_application_container(
    tmp_path: Path,
) -> None:
    (
        client_config_path,
        clients_folder_path,
    ) = create_valid_production_paths(
        tmp_path
    )

    configuration = create_configuration(
        client_config_path=client_config_path,
        clients_folder_path=clients_folder_path,
    )

    report_service = (
        FakeDailyPortfolioReportService()
    )

    application = build_application(
        configuration=configuration,
        daily_portfolio_report_service=(
            report_service
        ),
    )

    assert isinstance(
        application,
        ApplicationContainer,
    )

    assert isinstance(
        application.daily_production_runner,
        DailyProductionRunner,
    )

    assert (
        application.daily_portfolio_report_service
        is report_service
    )


def test_build_application_wires_real_repositories(
    tmp_path: Path,
) -> None:
    (
        client_config_path,
        clients_folder_path,
    ) = create_valid_production_paths(
        tmp_path
    )

    configuration = create_configuration(
        client_config_path=client_config_path,
        clients_folder_path=clients_folder_path,
    )

    application = build_application(
        configuration=configuration,
        daily_portfolio_report_service=(
            FakeDailyPortfolioReportService()
        ),
    )

    production_services = (
        application.production_services
    )

    runner = (
        production_services.daily_production_runner
    )

    assert runner is not None

    registry_repository = (
        runner._client_registry_repository
    )

    portfolio_repository = (
        runner._client_portfolio_repository
    )

    assert isinstance(
        registry_repository,
        PEV24ClientRegistryRepository,
    )

    assert isinstance(
        portfolio_repository,
        PEV24ClientPortfolioRepository,
    )

    assert (
        registry_repository.csv_path
        == str(client_config_path)
    )

    assert (
        portfolio_repository.clients_folder_path
        == str(clients_folder_path)
    )


def test_build_application_rejects_missing_client_config_key(
    tmp_path: Path,
) -> None:
    clients_folder_path = (
        tmp_path / "clients"
    )

    clients_folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    configuration = Configuration(
        values={
            PEV24_CLIENTS_FOLDER_PATH_KEY: str(
                clients_folder_path
            )
        }
    )

    with pytest.raises(
        ConfigurationError,
        match=PEV24_CLIENT_CONFIG_PATH_KEY,
    ):
        build_application(
            configuration=configuration
        )


def test_build_application_rejects_missing_clients_folder_key(
    tmp_path: Path,
) -> None:
    client_config_path = (
        tmp_path / "client_config.csv"
    )

    client_config_path.write_text(
        "Client,Capital,CashPercent\n",
        encoding="utf-8-sig",
    )

    configuration = Configuration(
        values={
            PEV24_CLIENT_CONFIG_PATH_KEY: str(
                client_config_path
            )
        }
    )

    with pytest.raises(
        ConfigurationError,
        match=PEV24_CLIENTS_FOLDER_PATH_KEY,
    ):
        build_application(
            configuration=configuration
        )


def test_build_application_rejects_missing_client_config_file(
    tmp_path: Path,
) -> None:
    missing_client_config_path = (
        tmp_path / "missing_client_config.csv"
    )

    clients_folder_path = (
        tmp_path / "clients"
    )

    clients_folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    configuration = create_configuration(
        client_config_path=(
            missing_client_config_path
        ),
        clients_folder_path=(
            clients_folder_path
        ),
    )

    with pytest.raises(
        ConfigurationError,
        match=(
            "Configured file does not exist"
        ),
    ):
        build_application(
            configuration=configuration
        )


def test_build_application_rejects_missing_clients_directory(
    tmp_path: Path,
) -> None:
    client_config_path = (
        tmp_path / "client_config.csv"
    )

    client_config_path.write_text(
        "Client,Capital,CashPercent\n",
        encoding="utf-8-sig",
    )

    missing_clients_folder_path = (
        tmp_path / "missing_clients"
    )

    configuration = create_configuration(
        client_config_path=(
            client_config_path
        ),
        clients_folder_path=(
            missing_clients_folder_path
        ),
    )

    with pytest.raises(
        ConfigurationError,
        match=(
            "Configured directory does not exist"
        ),
    ):
        build_application(
            configuration=configuration
        )


def test_build_application_normalizes_paths(
    tmp_path: Path,
) -> None:
    (
        client_config_path,
        clients_folder_path,
    ) = create_valid_production_paths(
        tmp_path
    )

    configuration = Configuration(
        values={
            PEV24_CLIENT_CONFIG_PATH_KEY: (
                f"  {client_config_path}  "
            ),
            PEV24_CLIENTS_FOLDER_PATH_KEY: (
                f"  {clients_folder_path}  "
            ),
        }
    )

    application = build_application(
        configuration=configuration,
        daily_portfolio_report_service=(
            FakeDailyPortfolioReportService()
        ),
    )

    runner = application.daily_production_runner

    assert runner is not None

    assert (
        runner._client_registry_repository.csv_path
        == str(client_config_path)
    )

    assert (
        runner
        ._client_portfolio_repository
        .clients_folder_path
        == str(clients_folder_path)
    )


def test_bootstrapped_runner_processes_real_csv_files(
    tmp_path: Path,
) -> None:
    client_config_path = (
        tmp_path / "client_config.csv"
    )

    clients_folder_path = (
        tmp_path / "clients"
    )

    clients_folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_client_config(
        file_path=client_config_path,
        rows=[
            "anh_dung,100000000,0.25",
            "chi_lan,200000000,0.10",
        ],
    )

    anh_dung_path = write_client_portfolio(
        folder=clients_folder_path,
        client_id="anh_dung",
    )

    chi_lan_path = write_client_portfolio(
        folder=clients_folder_path,
        client_id="chi_lan",
    )

    configuration = create_configuration(
        client_config_path=client_config_path,
        clients_folder_path=clients_folder_path,
    )

    report_service = (
        FakeDailyPortfolioReportService(
            report_text="TELEGRAM READY REPORT"
        )
    )

    application = build_application(
        configuration=configuration,
        daily_portfolio_report_service=(
            report_service
        ),
    )

    runner = application.daily_production_runner

    assert runner is not None

    result = runner.run()

    assert result.succeeded is True
    assert result.total_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    assert result.reports_by_client == {
        "anh_dung": "TELEGRAM READY REPORT",
        "chi_lan": "TELEGRAM READY REPORT",
    }

    assert report_service.calls == [
        str(anh_dung_path),
        str(chi_lan_path),
    ]


def test_bootstrapped_runner_reports_missing_portfolio(
    tmp_path: Path,
) -> None:
    client_config_path = (
        tmp_path / "client_config.csv"
    )

    clients_folder_path = (
        tmp_path / "clients"
    )

    clients_folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_client_config(
        file_path=client_config_path,
        rows=[
            "anh_dung,100000000,0.25",
        ],
    )

    configuration = create_configuration(
        client_config_path=client_config_path,
        clients_folder_path=clients_folder_path,
    )

    application = build_application(
        configuration=configuration,
        daily_portfolio_report_service=(
            FakeDailyPortfolioReportService()
        ),
    )

    runner = application.daily_production_runner

    assert runner is not None

    result = runner.run()

    assert result.succeeded is False
    assert result.total_count == 1
    assert result.success_count == 0
    assert result.failure_count == 1

    client_result = result.results[0]

    assert client_result.client_id == "anh_dung"
    assert client_result.success is False
    assert client_result.error is not None

    assert "portfolio file not found" in (
        client_result.error
    )


def test_build_application_rejects_configuration_and_provider_together(
    tmp_path: Path,
) -> None:
    from infrastructure.configuration import (
        ConfigurationProvider,
    )

    (
        client_config_path,
        clients_folder_path,
    ) = create_valid_production_paths(
        tmp_path
    )

    configuration = create_configuration(
        client_config_path=client_config_path,
        clients_folder_path=clients_folder_path,
    )

    provider = ConfigurationProvider(
        configuration=configuration
    )

    with pytest.raises(
        ValueError,
        match=(
            "provide either configuration or "
            "configuration_provider, not both"
        ),
    ):
        build_application(
            configuration=configuration,
            configuration_provider=provider,
        )