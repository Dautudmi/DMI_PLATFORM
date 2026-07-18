from __future__ import annotations

from typing import Any

from apps.portfolio.services.daily_portfolio_report_service import (
    DailyPortfolioReportService,
)
from apps.portfolio.services.daily_production_runner import (
    DailyProductionRunner,
)
from apps.portfolio.services.portfolio_production_flow_service import (
    PortfolioProductionFlowService,
)


class ProductionServiceContainer:
    """
    Container dành riêng cho Production Services.

    Responsibility:
    - khởi tạo DailyPortfolioReportService
    - khởi tạo DailyProductionRunner khi đủ dependency
    - khởi tạo PortfolioProductionFlowService khi đủ dependency
    - giữ wiring production tách khỏi analysis services

    Không:
    - chứa business logic
    - hard-code đường dẫn
    - đọc environment variables
    - chạy production flow
    - gửi Telegram
    - chạy Scheduler

    Các service phụ thuộc Repository chỉ được tạo khi
    dependency tương ứng được cung cấp.
    """

    def __init__(
        self,
        client_registry_repository: Any | None = None,
        client_portfolio_repository: Any | None = None,
        portfolio_transaction_service: Any | None = None,
        daily_portfolio_report_service: Any | None = None,
    ) -> None:
        self.daily_portfolio_report_service = (
            daily_portfolio_report_service
            or DailyPortfolioReportService()
        )

        self.daily_production_runner = (
            self._create_daily_production_runner(
                client_registry_repository=(
                    client_registry_repository
                ),
                client_portfolio_repository=(
                    client_portfolio_repository
                ),
            )
        )

        self.portfolio_production_flow_service = (
            self._create_portfolio_production_flow_service(
                portfolio_transaction_service=(
                    portfolio_transaction_service
                )
            )
        )

    def _create_daily_production_runner(
        self,
        client_registry_repository: Any | None,
        client_portfolio_repository: Any | None,
    ) -> DailyProductionRunner | None:
        """
        Tạo DailyProductionRunner khi có đủ hai Repository.

        Nếu cả hai dependency đều chưa được cung cấp,
        trả về None để ApplicationContainer mặc định
        vẫn hoạt động như trước.

        Nếu chỉ có một dependency, raise ValueError vì
        container đang ở trạng thái cấu hình không hợp lệ.
        """

        if (
            client_registry_repository is None
            and client_portfolio_repository is None
        ):
            return None

        if client_registry_repository is None:
            raise ValueError(
                "client_registry_repository is required "
                "when client_portfolio_repository is provided"
            )

        if client_portfolio_repository is None:
            raise ValueError(
                "client_portfolio_repository is required "
                "when client_registry_repository is provided"
            )

        return DailyProductionRunner(
            client_registry_repository=(
                client_registry_repository
            ),
            client_portfolio_repository=(
                client_portfolio_repository
            ),
            daily_portfolio_report_service=(
                self.daily_portfolio_report_service
            ),
        )

    def _create_portfolio_production_flow_service(
        self,
        portfolio_transaction_service: Any | None,
    ) -> PortfolioProductionFlowService | None:
        """
        Tạo PortfolioProductionFlowService khi có
        PortfolioTransactionService.

        DailyPortfolioReportService luôn có sẵn trong
        ProductionServiceContainer.
        """

        if portfolio_transaction_service is None:
            return None

        return PortfolioProductionFlowService(
            portfolio_transaction_service=(
                portfolio_transaction_service
            ),
            daily_portfolio_report_service=(
                self.daily_portfolio_report_service
            ),
        )