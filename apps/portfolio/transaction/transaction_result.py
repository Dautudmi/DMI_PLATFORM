from dataclasses import dataclass

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.transaction import Transaction


@dataclass(frozen=True, slots=True)
class TransactionResult:
    success: bool
    transaction: Transaction
    portfolio: Portfolio | None = None
    message: str | None = None
    error: str | None = None