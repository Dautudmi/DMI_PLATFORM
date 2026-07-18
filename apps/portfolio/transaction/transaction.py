from dataclasses import dataclass
from datetime import datetime

from apps.portfolio.transaction.transaction_type import (
    TransactionType,
)


@dataclass(frozen=True, slots=True)
class Transaction:
    """
    Giao dịch danh mục cơ sở.

    Domain object này không biết:
    - CSV
    - Repository
    - Telegram
    - Application Service
    """

    client_id: str
    symbol: str
    quantity: float
    price: float
    transaction_type: TransactionType
    executed_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_client_id = str(self.client_id).strip()
        normalized_symbol = str(self.symbol).strip().upper()

        if not normalized_client_id:
            raise ValueError("client_id must not be empty")

        if not normalized_symbol:
            raise ValueError("symbol must not be empty")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than 0")

        if self.price < 0:
            raise ValueError("price must not be negative")

        if not isinstance(
            self.transaction_type,
            TransactionType,
        ):
            raise ValueError(
                "transaction_type must be TransactionType"
            )

        object.__setattr__(
            self,
            "client_id",
            normalized_client_id,
        )

        object.__setattr__(
            self,
            "symbol",
            normalized_symbol,
        )

    @property
    def gross_value(self) -> float:
        return self.quantity * self.price