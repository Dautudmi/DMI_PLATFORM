from __future__ import annotations

from typing import Any

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.portfolio_production_flow_result import (
    PortfolioProductionFlowResult,
)
from apps.portfolio.transaction.transaction import Transaction


class PortfolioProductionFlowService:
    """
    Application Service điều phối một giao dịch Production.

    Flow:

    Portfolio + Transaction
        ↓
    PortfolioTransactionService
        ↓
    TransactionService
        ↓
    PositionEngine
        ↓
    Trade History Repository
        ↓
    PEV24PortfolioWriter
        ↓
    client_<client_id>.csv
        ↓
    DailyPortfolioReportService
        ↓
    Telegram-ready report text

    Responsibility:
    - gọi PortfolioTransactionService
    - kiểm tra kết quả Transaction Flow
    - lấy đường dẫn Portfolio vừa được ghi
    - gọi DailyPortfolioReportService
    - trả về Production Flow Result

    Không:
    - áp dụng Transaction trực tiếp
    - tính Average Cost
    - sửa Position
    - ghi Trade History trực tiếp
    - ghi Portfolio trực tiếp
    - tính Health trực tiếp
    - gọi Core Engine trực tiếp
    - gửi Telegram trực tiếp
    """

    def __init__(
        self,
        portfolio_transaction_service: Any,
        daily_portfolio_report_service: Any,
    ) -> None:
        if portfolio_transaction_service is None:
            raise ValueError(
                "portfolio_transaction_service must not be None"
            )

        if daily_portfolio_report_service is None:
            raise ValueError(
                "daily_portfolio_report_service must not be None"
            )

        self._portfolio_transaction_service = (
            portfolio_transaction_service
        )
        self._daily_portfolio_report_service = (
            daily_portfolio_report_service
        )

    def execute(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> PortfolioProductionFlowResult:
        """
        Thực hiện toàn bộ Production Flow cho một giao dịch.

        Args:
            portfolio:
                Portfolio hiện tại trước giao dịch.

            transaction:
                Giao dịch BUY hoặc SELL cần áp dụng.

        Returns:
            PortfolioProductionFlowResult.
        """

        if portfolio is None:
            raise ValueError("portfolio must not be None")

        if transaction is None:
            raise ValueError("transaction must not be None")

        try:
            transaction_result = self._execute_transaction_flow(
                portfolio=portfolio,
                transaction=transaction,
            )

            if not transaction_result.success:
                return PortfolioProductionFlowResult(
                    success=False,
                    transaction=transaction,
                    portfolio=None,
                    transaction_result=transaction_result,
                    portfolio_file_path=None,
                    report_text=None,
                    message=None,
                    error=(
                        transaction_result.error
                        or "portfolio transaction flow failed"
                    ),
                )

            updated_portfolio = transaction_result.portfolio

            if updated_portfolio is None:
                return PortfolioProductionFlowResult(
                    success=False,
                    transaction=transaction,
                    portfolio=None,
                    transaction_result=transaction_result,
                    portfolio_file_path=None,
                    report_text=None,
                    message=None,
                    error=(
                        "portfolio transaction flow succeeded "
                        "but returned no portfolio"
                    ),
                )

            write_result = transaction_result.write_result

            if write_result is None:
                return PortfolioProductionFlowResult(
                    success=False,
                    transaction=transaction,
                    portfolio=updated_portfolio,
                    transaction_result=transaction_result,
                    portfolio_file_path=None,
                    report_text=None,
                    message=None,
                    error=(
                        "portfolio transaction flow succeeded "
                        "but returned no write result"
                    ),
                )

            if not write_result.success:
                return PortfolioProductionFlowResult(
                    success=False,
                    transaction=transaction,
                    portfolio=updated_portfolio,
                    transaction_result=transaction_result,
                    portfolio_file_path=None,
                    report_text=None,
                    message=None,
                    error=(
                        write_result.error
                        or "portfolio write failed"
                    ),
                )

            portfolio_file_path = self._normalize_file_path(
                write_result.file_path
            )

            report_text = self._generate_report(
                portfolio_file_path
            )

            if report_text is None:
                return PortfolioProductionFlowResult(
                    success=False,
                    transaction=transaction,
                    portfolio=updated_portfolio,
                    transaction_result=transaction_result,
                    portfolio_file_path=portfolio_file_path,
                    report_text=None,
                    message=None,
                    error=(
                        "daily portfolio report service "
                        "returned None"
                    ),
                )

            normalized_report_text = str(report_text).strip()

            if not normalized_report_text:
                return PortfolioProductionFlowResult(
                    success=False,
                    transaction=transaction,
                    portfolio=updated_portfolio,
                    transaction_result=transaction_result,
                    portfolio_file_path=portfolio_file_path,
                    report_text=None,
                    message=None,
                    error=(
                        "daily portfolio report service "
                        "returned empty report"
                    ),
                )

            return PortfolioProductionFlowResult(
                success=True,
                transaction=transaction,
                portfolio=updated_portfolio,
                transaction_result=transaction_result,
                portfolio_file_path=portfolio_file_path,
                report_text=normalized_report_text,
                message=(
                    f"Production portfolio flow completed "
                    f"for client "
                    f"{updated_portfolio.client_name}"
                ),
                error=None,
            )

        except Exception as exc:
            return PortfolioProductionFlowResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                transaction_result=None,
                portfolio_file_path=None,
                report_text=None,
                message=None,
                error=str(exc),
            )

    def _execute_transaction_flow(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> Any:
        if not hasattr(
            self._portfolio_transaction_service,
            "execute",
        ):
            raise AttributeError(
                "portfolio_transaction_service must have "
                "execute method"
            )

        return self._portfolio_transaction_service.execute(
            portfolio=portfolio,
            transaction=transaction,
        )

    def _generate_report(
        self,
        portfolio_file_path: str,
    ) -> str:
        if not hasattr(
            self._daily_portfolio_report_service,
            "generate",
        ):
            raise AttributeError(
                "daily_portfolio_report_service must have "
                "generate method"
            )

        return self._daily_portfolio_report_service.generate(
            portfolio_file_path
        )

    def _normalize_file_path(
        self,
        file_path: str,
    ) -> str:
        if file_path is None or not str(file_path).strip():
            raise ValueError(
                "portfolio write result file_path "
                "must not be empty"
            )

        return str(file_path).strip()