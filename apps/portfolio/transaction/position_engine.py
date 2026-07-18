from copy import deepcopy

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.transaction import Transaction
from apps.portfolio.transaction.transaction_result import (
    TransactionResult,
)
from apps.portfolio.transaction.transaction_type import (
    TransactionType,
)


class PositionEngine:
    """
    Áp dụng giao dịch vào Portfolio Domain.

    Responsibility:
    - mua mới vị thế
    - mua thêm vị thế
    - bán một phần vị thế
    - bán toàn bộ vị thế
    - cập nhật cash
    - tính lại average cost khi mua

    Không đọc hoặc ghi CSV.
    Không gọi Repository.
    Không render.
    Không orchestration bên ngoài Domain.
    """

    def apply(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> TransactionResult:
        if portfolio is None:
            raise ValueError("portfolio must not be None")

        if transaction is None:
            raise ValueError("transaction must not be None")

        if (
            str(portfolio.client_name).strip()
            != transaction.client_id
        ):
            return TransactionResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                message=None,
                error=(
                    "transaction client_id does not match "
                    "portfolio client_name"
                ),
            )

        portfolio_copy = deepcopy(portfolio)

        try:
            if (
                transaction.transaction_type
                == TransactionType.BUY
            ):
                self._apply_buy(
                    portfolio=portfolio_copy,
                    transaction=transaction,
                )

            elif (
                transaction.transaction_type
                == TransactionType.SELL
            ):
                self._apply_sell(
                    portfolio=portfolio_copy,
                    transaction=transaction,
                )

            else:
                raise ValueError(
                    "unsupported transaction type"
                )

            return TransactionResult(
                success=True,
                transaction=transaction,
                portfolio=portfolio_copy,
                message=(
                    f"{transaction.transaction_type.value} "
                    f"{transaction.symbol} applied successfully"
                ),
                error=None,
            )

        except Exception as exc:
            return TransactionResult(
                success=False,
                transaction=transaction,
                portfolio=None,
                message=None,
                error=str(exc),
            )

    def _apply_buy(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> None:
        required_cash = transaction.gross_value

        if portfolio.cash < required_cash:
            raise ValueError(
                "insufficient cash for buy transaction"
            )

        holding = self._find_holding(
            portfolio=portfolio,
            symbol=transaction.symbol,
        )

        if holding is None:
            portfolio.holdings.append(
                Holding(
                    symbol=transaction.symbol,
                    quantity=transaction.quantity,
                    average_cost=transaction.price,
                    current_price=None,
                )
            )

        else:
            old_total_cost = (
                holding.quantity
                * holding.average_cost
            )

            new_transaction_cost = (
                transaction.quantity
                * transaction.price
            )

            new_quantity = (
                holding.quantity
                + transaction.quantity
            )

            holding.average_cost = (
                old_total_cost
                + new_transaction_cost
            ) / new_quantity

            holding.quantity = new_quantity

        portfolio.cash -= required_cash

    def _apply_sell(
        self,
        portfolio: Portfolio,
        transaction: Transaction,
    ) -> None:
        holding = self._find_holding(
            portfolio=portfolio,
            symbol=transaction.symbol,
        )

        if holding is None:
            raise ValueError(
                f"holding not found for symbol "
                f"{transaction.symbol}"
            )

        if holding.quantity < transaction.quantity:
            raise ValueError(
                "insufficient holding quantity for sell transaction"
            )

        holding.quantity -= transaction.quantity
        portfolio.cash += transaction.gross_value

        if holding.quantity == 0:
            portfolio.holdings.remove(holding)

    def _find_holding(
        self,
        portfolio: Portfolio,
        symbol: str,
    ) -> Holding | None:
        normalized_symbol = str(symbol).strip().upper()

        for holding in portfolio.holdings:
            if (
                str(holding.symbol).strip().upper()
                == normalized_symbol
            ):
                return holding

        return None