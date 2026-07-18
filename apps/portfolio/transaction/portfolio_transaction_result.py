from dataclasses import dataclass

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.transaction import Transaction
from infrastructure.pe_v24.pe_v24_portfolio_write_result import (
    PEV24PortfolioWriteResult,
)
from infrastructure.portfolio.transaction_record import (
    TransactionRecord,
)


@dataclass(frozen=True, slots=True)
class PortfolioTransactionResult:
    success: bool
    transaction: Transaction
    portfolio: Portfolio | None = None
    record: TransactionRecord | None = None
    write_result: PEV24PortfolioWriteResult | None = None
    message: str | None = None
    error: str | None = None