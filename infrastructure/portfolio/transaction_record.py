from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TransactionRecord:
    """
    Bản ghi giao dịch được lưu trong Trade History.

    Đây là DTO thuộc Infrastructure, không phải Portfolio Domain.
    """

    trade_id: str
    executed_at: datetime
    client_id: str
    transaction_type: str
    symbol: str
    quantity: float
    price: float
    gross_value: float

    def __post_init__(self) -> None:
        normalized_trade_id = str(self.trade_id).strip()
        normalized_client_id = str(self.client_id).strip()
        normalized_transaction_type = (
            str(self.transaction_type).strip().upper()
        )
        normalized_symbol = str(self.symbol).strip().upper()

        if not normalized_trade_id:
            raise ValueError("trade_id must not be empty")

        if not isinstance(self.executed_at, datetime):
            raise ValueError("executed_at must be datetime")

        if not normalized_client_id:
            raise ValueError("client_id must not be empty")

        if normalized_transaction_type not in {"BUY", "SELL"}:
            raise ValueError(
                "transaction_type must be BUY or SELL"
            )

        if not normalized_symbol:
            raise ValueError("symbol must not be empty")

        if self.quantity <= 0:
            raise ValueError(
                "quantity must be greater than 0"
            )

        if self.price < 0:
            raise ValueError("price must not be negative")

        if self.gross_value < 0:
            raise ValueError(
                "gross_value must not be negative"
            )

        object.__setattr__(
            self,
            "trade_id",
            normalized_trade_id,
        )
        object.__setattr__(
            self,
            "client_id",
            normalized_client_id,
        )
        object.__setattr__(
            self,
            "transaction_type",
            normalized_transaction_type,
        )
        object.__setattr__(
            self,
            "symbol",
            normalized_symbol,
        )