from __future__ import annotations

from dataclasses import dataclass

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.portfolio_transaction_result import (
    PortfolioTransactionResult,
)
from apps.portfolio.transaction.transaction import Transaction


@dataclass(frozen=True, slots=True)
class PortfolioProductionFlowResult:
    """
    Kết quả của một Production Portfolio Flow.

    Flow:

    Portfolio + Transaction
        ↓
    PortfolioTransactionService
        ↓
    Trade History
        ↓
    Portfolio Writer
        ↓
    Daily Portfolio Report
        ↓
    Telegram-ready text

    Đây là Application Result.

    Không chứa Business Logic.
    Không tự áp dụng Transaction.
    Không tự ghi file.
    Không tự render báo cáo.
    """

    success: bool
    transaction: Transaction

    portfolio: Portfolio | None = None

    transaction_result: PortfolioTransactionResult | None = None

    portfolio_file_path: str | None = None

    report_text: str | None = None

    message: str | None = None

    error: str | None = None