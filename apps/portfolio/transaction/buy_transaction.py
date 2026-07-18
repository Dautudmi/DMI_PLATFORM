from datetime import datetime

from apps.portfolio.transaction.transaction import Transaction
from apps.portfolio.transaction.transaction_type import (
    TransactionType,
)


class BuyTransaction(Transaction):
    """
    Giao dịch mua cổ phiếu.
    """

    def __init__(
        self,
        client_id: str,
        symbol: str,
        quantity: float,
        price: float,
        executed_at: datetime | None = None,
    ):
        super().__init__(
            client_id=client_id,
            symbol=symbol,
            quantity=quantity,
            price=price,
            transaction_type=TransactionType.BUY,
            executed_at=executed_at,
        )