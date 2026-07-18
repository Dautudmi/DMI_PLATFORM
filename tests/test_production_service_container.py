from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from apps.portfolio.services.daily_portfolio_report_service import (
    DailyPortfolioReportService,
)
from apps.portfolio.services.daily_production_runner import (
    DailyProductionRunner,
)
from apps.portfolio.services.portfolio_production_flow_service import (
    PortfolioProductionFlowService,
)
from apps.shared.containers.application import (
    ApplicationContainer,
)
from apps.shared.containers.production_services import (
    ProductionServiceContainer,
)


class FakeClientRegistryRepository:
    def load_client_ids(self) -> list[str]:
        return []


class FakeClientPortfolioRepository:
    def get_portfolio_path(
        self,
        client_id: str,
    ) -> str:
        return f"client_{client_id}.csv"

    def exists(
        self,
        client_id: str,
    ) -> bool:
        return False


class FakePortfolioTransactionService:
    def execute(
        self,
        portfolio: Any,
        transaction: Any,
    ) -> Any:
        raise NotImplementedError


class FakeDailyPortfolioReportService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def generate(
        self,
        csv_file: str | Path,
    ) -> str:
        path = str(csv_file)
        self.calls.append(path)

        return "FAKE REPORT"


def test_default_production_container_creates_report_service() -> None:
    container = ProductionServiceContainer()

    assert isinstance(
        container.daily_portfolio_report_service,
        DailyPortfolioReportService,
    )

    assert container.daily_production_runner is None

    assert (
        container.portfolio_production_flow_service
        is None
    )


def test_production_container_uses_injected_report_service() -> None:
    report_service = FakeDailyPortfolioReportService()

    container = ProductionServiceContainer(
        daily_portfolio_report_service=(
            report_service
        )
    )

    assert (
        container.daily_portfolio_report_service
        is report_service
    )


def test_creates_daily_runner_when_repositories_are_provided() -> None:
    registry_repository = (
        FakeClientRegistryRepository()
    )

    portfolio_repository = (
        FakeClientPortfolioRepository()
    )

    report_service = (
        FakeDailyPortfolioReportService()
    )

    container = ProductionServiceContainer(
        client_registry_repository=(
            registry_repository
        ),
        client_portfolio_repository=(
            portfolio_repository
        ),
        daily_portfolio_report_service=(
            report_service
        ),
    )

    assert isinstance(
        container.daily_production_runner,
        DailyProductionRunner,
    )

    assert (
        container.daily_portfolio_report_service
        is report_service
    )

    result = container.daily_production_runner.run()

    assert result.succeeded is True
    assert result.total_count == 0


def test_rejects_registry_without_portfolio_repository() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "client_portfolio_repository is required "
            "when client_registry_repository is provided"
        ),
    ):
        ProductionServiceContainer(
            client_registry_repository=(
                FakeClientRegistryRepository()
            ),
            client_portfolio_repository=None,
        )


def test_rejects_portfolio_repository_without_registry() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "client_registry_repository is required "
            "when client_portfolio_repository is provided"
        ),
    ):
        ProductionServiceContainer(
            client_registry_repository=None,
            client_portfolio_repository=(
                FakeClientPortfolioRepository()
            ),
        )


def test_creates_production_flow_when_transaction_service_is_provided() -> None:
    transaction_service = (
        FakePortfolioTransactionService()
    )

    report_service = (
        FakeDailyPortfolioReportService()
    )

    container = ProductionServiceContainer(
        portfolio_transaction_service=(
            transaction_service
        ),
        daily_portfolio_report_service=(
            report_service
        ),
    )

    assert isinstance(
        container.portfolio_production_flow_service,
        PortfolioProductionFlowService,
    )

    assert (
        container.daily_portfolio_report_service
        is report_service
    )


def test_default_application_container_remains_backward_compatible() -> None:
    container = ApplicationContainer()

    assert container.providers is not None
    assert container.services is not None
    assert container.production_services is not None

    assert container.financial_provider is (
        container.providers.financial_provider
    )

    assert container.position_analyzer is (
        container.services.position_analyzer
    )

    assert container.dmi_service is (
        container.services.dmi_service
    )

    assert container.holding_pipeline is (
        container.services.holding_pipeline
    )

    assert container.holding_analyzer is (
        container.services.holding_analyzer
    )

    assert container.portfolio_analyzer is (
        container.services.portfolio_analyzer
    )

    assert (
        container.daily_portfolio_report_service
        is container.production_services
        .daily_portfolio_report_service
    )

    assert container.daily_production_runner is None

    assert (
        container.portfolio_production_flow_service
        is None
    )


def test_application_container_wires_daily_production_runner() -> None:
    registry_repository = (
        FakeClientRegistryRepository()
    )

    portfolio_repository = (
        FakeClientPortfolioRepository()
    )

    report_service = (
        FakeDailyPortfolioReportService()
    )

    container = ApplicationContainer(
        client_registry_repository=(
            registry_repository
        ),
        client_portfolio_repository=(
            portfolio_repository
        ),
        daily_portfolio_report_service=(
            report_service
        ),
    )

    assert isinstance(
        container.daily_production_runner,
        DailyProductionRunner,
    )

    assert (
        container.daily_production_runner
        is container.production_services
        .daily_production_runner
    )

    assert (
        container.daily_portfolio_report_service
        is report_service
    )


def test_application_container_wires_transaction_production_flow() -> None:
    transaction_service = (
        FakePortfolioTransactionService()
    )

    report_service = (
        FakeDailyPortfolioReportService()
    )

    container = ApplicationContainer(
        portfolio_transaction_service=(
            transaction_service
        ),
        daily_portfolio_report_service=(
            report_service
        ),
    )

    assert isinstance(
        container.portfolio_production_flow_service,
        PortfolioProductionFlowService,
    )

    assert (
        container.portfolio_production_flow_service
        is container.production_services
        .portfolio_production_flow_service
    )