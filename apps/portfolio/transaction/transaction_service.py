from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.position_engine import (
    PositionEngine,
)
from apps.portfolio.transaction.transaction import Transaction
from apps.portfolio.transaction.transaction_service_result import (
    TransactionServiceResult,
)
from infrastructure.portfolio.transaction_record import (
    TransactionRecord,
)


class TransactionService:
    """
    Orchestration Service cho một giao dịch Portfolio.

    Luồng:

    Portfolio
        +
    Transaction
        ↓
    PositionEngine
        ↓
    Portfolio mới
        ↓
    TransactionRepository
        ↓
    Trade History

    Quy tắc an toàn:
    - chỉ lưu lịch sử khi PositionEngine thành công
    - nếu lưu history lỗi, Service báo thất bại
    - không tự ghi file danh mục khách
    """

    def __init__(
        self,
        position_engine: PositionEngine,
        transaction_repository: Any,
        clock: Any | None = None,
        trade_id_factory: Any | None = None,
    ):
        if position_engine is None:
            raise ValueError(
                "position_engine must not be None"
            )

        if transaction_repository is None:
            raise ValueError(
                "transaction_repository must not be None"
            )

        self._position_engine = position_engine
        self._transaction_repository = (
            transaction_repository
        )
        self._clock = clock
        self._trade_id_factory = trade_id_factory

    def execute(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> TransactionServiceResult:
        if portfolio is None:
            raise ValueError(
                "portfolio must not be None"
            )

        if transaction is None:
            raise ValueError(
                "transaction must not be None"
            )

        position_result = self._position_engine.apply(
            portfolio=portfolio,
            transaction=transaction,
        )

        if not position_result.success:
            return TransactionServiceResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                record=None,
                message=None,
                error=position_result.error,
            )

        try:
            record = self._build_record(transaction)

            self._append_record(record)

            return TransactionServiceResult(
                success=True,
                transaction=transaction,
                portfolio=position_result.portfolio,
                record=record,
                message=(
                    f"{transaction.transaction_type.value} "
                    f"{transaction.symbol} completed "
                    f"and recorded"
                ),
                error=None,
            )

        except Exception as exc:
            return TransactionServiceResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                record=None,
                message=None,
                error=str(exc),
            )

    def _build_record(
        self,
        transaction: Transaction,
    ) -> TransactionRecord:
        executed_at = (
            transaction.executed_at
            or self._now()
        )

        return TransactionRecord(
            trade_id=self._create_trade_id(),
            executed_at=executed_at,
            client_id=transaction.client_id,
            transaction_type=(
                transaction.transaction_type.value
            ),
            symbol=transaction.symbol,
            quantity=transaction.quantity,
            price=transaction.price,
            gross_value=transaction.gross_value,
        )

    def _append_record(
        self,
        record: TransactionRecord,
    ) -> None:
        if hasattr(
            self._transaction_repository,
            "append",
        ):
            self._transaction_repository.append(record)
            return

        raise AttributeError(
            "transaction_repository must have append method"
        )

    def _now(self) -> datetime:
        if self._clock is None:
            return datetime.now()

        if hasattr(self._clock, "now"):
            value = self._clock.now()

            if not isinstance(value, datetime):
                raise TypeError(
                    "clock.now must return datetime"
                )

            return value

        raise AttributeError(
            "clock must have now method"
        )

    def _create_trade_id(self) -> str:
        if self._trade_id_factory is None:
            return uuid4().hex

        if callable(self._trade_id_factory):
            trade_id = str(
                self._trade_id_factory()
            ).strip()

            if not trade_id:
                raise ValueError(
                    "trade_id_factory returned empty value"
                )

            return trade_id

        raise TypeError(
            "trade_id_factory must be callable"
        )