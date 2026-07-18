from dataclasses import dataclass

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.transaction import Transaction
from infrastructure.portfolio.transaction_record import (
    TransactionRecord,
)


@dataclass(frozen=True, slots=True)
class TransactionServiceResult:
    """
    Kết quả orchestration của TransactionService.
    """

    success: bool
    transaction: Transaction
    portfolio: Portfolio | None = None
    record: TransactionRecord | None = None
    message: str | None = None
    error: str | None = None