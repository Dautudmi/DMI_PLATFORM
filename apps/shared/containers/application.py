from __future__ import annotations

from typing import Any

from apps.portfolio.providers.financial_data_provider import (
    FinancialDataProvider,
)
from apps.shared.containers.production_services import (
    ProductionServiceContainer,
)
from apps.shared.containers.providers import (
    ProviderContainer,
)
from apps.shared.containers.services import (
    ServiceContainer,
)


class ApplicationContainer:
    """
    Application composition root.

    Container gốc của toàn bộ DMI Application.

    Structure:

    ApplicationContainer
        ├── ProviderContainer
        ├── ServiceContainer
        └── ProductionServiceContainer

    Responsibility:
    - wiring providers
    - wiring analysis services
    - wiring production services
    - cung cấp backward-compatible shortcuts

    Không:
    - chứa business logic
    - chạy Use Case
    - chạy Production Runner
    - đọc file cấu hình
    - hard-code đường dẫn
    """

    def __init__(
        self,
        financial_provider: FinancialDataProvider | None = None,
        client_registry_repository: Any | None = None,
        client_portfolio_repository: Any | None = None,
        portfolio_transaction_service: Any | None = None,
        daily_portfolio_report_service: Any | None = None,
    ) -> None:
        self.providers = ProviderContainer(
            financial_provider=financial_provider,
        )

        self.services = ServiceContainer(
            financial_provider=(
                self.providers.financial_provider
            ),
        )

        self.production_services = (
            ProductionServiceContainer(
                client_registry_repository=(
                    client_registry_repository
                ),
                client_portfolio_repository=(
                    client_portfolio_repository
                ),
                portfolio_transaction_service=(
                    portfolio_transaction_service
                ),
                daily_portfolio_report_service=(
                    daily_portfolio_report_service
                ),
            )
        )

        self._create_backward_compatible_shortcuts()

    def _create_backward_compatible_shortcuts(
        self,
    ) -> None:
        """
        Duy trì các attribute cũ để code hiện tại
        không cần thay đổi.
        """

        self.financial_provider = (
            self.providers.financial_provider
        )

        self.position_analyzer = (
            self.services.position_analyzer
        )

        self.dmi_service = self.services.dmi_service

        self.holding_pipeline = (
            self.services.holding_pipeline
        )

        self.holding_analyzer = (
            self.services.holding_analyzer
        )

        self.portfolio_analyzer = (
            self.services.portfolio_analyzer
        )

        self.daily_portfolio_report_service = (
            self.production_services
            .daily_portfolio_report_service
        )

        self.daily_production_runner = (
            self.production_services
            .daily_production_runner
        )

        self.portfolio_production_flow_service = (
            self.production_services
            .portfolio_production_flow_service
        )