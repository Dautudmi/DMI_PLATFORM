from typing import Any

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.portfolio_transaction_result import (
    PortfolioTransactionResult,
)
from apps.portfolio.transaction.transaction import (
    Transaction,
)


class PortfolioTransactionService:
    """
    Orchestration Service hoàn chỉnh cho một giao dịch.

    Luồng:

    Portfolio + Transaction
        ↓
    TransactionService
        ↓
    PositionEngine
        ↓
    Trade History
        ↓
    Portfolio Writer
        ↓
    client_<client_id>.csv

    TransactionService vẫn chịu trách nhiệm:
    - áp dụng giao dịch
    - ghi Trade History

    PortfolioTransactionService chịu trách nhiệm:
    - gọi TransactionService
    - ghi Portfolio mới về storage
    """

    def __init__(
        self,
        transaction_service: Any,
        portfolio_writer: Any,
    ):
        if transaction_service is None:
            raise ValueError(
                "transaction_service must not be None"
            )

        if portfolio_writer is None:
            raise ValueError(
                "portfolio_writer must not be None"
            )

        self._transaction_service = transaction_service
        self._portfolio_writer = portfolio_writer

    def execute(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> PortfolioTransactionResult:
        if portfolio is None:
            raise ValueError(
                "portfolio must not be None"
            )

        if transaction is None:
            raise ValueError(
                "transaction must not be None"
            )

        transaction_result = (
            self._execute_transaction(
                portfolio=portfolio,
                transaction=transaction,
            )
        )

        if not transaction_result.success:
            return PortfolioTransactionResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                record=None,
                write_result=None,
                message=None,
                error=transaction_result.error,
            )

        try:
            write_result = self._write_portfolio(
                transaction_result.portfolio
            )

            if not write_result.success:
                return PortfolioTransactionResult(
                    success=False,
                    transaction=transaction,
                    portfolio=None,
                    record=transaction_result.record,
                    write_result=write_result,
                    message=None,
                    error=write_result.error,
                )

            return PortfolioTransactionResult(
                success=True,
                transaction=transaction,
                portfolio=transaction_result.portfolio,
                record=transaction_result.record,
                write_result=write_result,
                message=(
                    f"{transaction.transaction_type.value} "
                    f"{transaction.symbol} completed, "
                    f"recorded and portfolio updated"
                ),
                error=None,
            )

        except Exception as exc:
            return PortfolioTransactionResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                record=transaction_result.record,
                write_result=None,
                message=None,
                error=str(exc),
            )

    def _execute_transaction(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ):
        if hasattr(
            self._transaction_service,
            "execute",
        ):
            return self._transaction_service.execute(
                portfolio=portfolio,
                transaction=transaction,
            )

        raise AttributeError(
            "transaction_service must have execute method"
        )

    def _write_portfolio(
        self,
        portfolio: Portfolio,
    ):
        if hasattr(
            self._portfolio_writer,
            "write",
        ):
            return self._portfolio_writer.write(
                portfolio
            )

        raise AttributeError(
            "portfolio_writer must have write method"
        )