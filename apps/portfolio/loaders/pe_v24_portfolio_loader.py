from collections.abc import Iterable

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from infrastructure.pe_v24.pe_v24_client_config import (
    PEV24ClientConfig,
)
from infrastructure.pe_v24.pe_v24_client_position import (
    PEV24ClientPosition,
)


class PEV24PortfolioLoader:
    """
    Chuyển dữ liệu PE_V2.4 thành Portfolio Domain của DMI.

    Input:
    - PEV24ClientConfig
    - danh sách PEV24ClientPosition

    Output:
    - Portfolio Domain

    Responsibility:
    - map client config sang Portfolio
    - map position sang Holding
    - tính số tiền mặt từ Capital và CashPercent

    Không đọc CSV.
    Không gọi Repository.
    Không orchestration.
    Không tính Health/Recommendation/Decision.
    """

    def load(
        self,
        client_config: PEV24ClientConfig,
        positions: Iterable[PEV24ClientPosition],
    ) -> Portfolio:
        if client_config is None:
            raise ValueError(
                "client_config must not be None"
            )

        if positions is None:
            raise ValueError("positions must not be None")

        client_name = str(
            client_config.client_id
        ).strip()

        if not client_name:
            raise ValueError(
                "client_config.client_id must not be empty"
            )

        capital = float(client_config.capital)
        cash_percent = float(client_config.cash_percent)

        if capital < 0:
            raise ValueError(
                "client_config.capital must not be negative"
            )

        if cash_percent < 0 or cash_percent > 1:
            raise ValueError(
                "client_config.cash_percent must be "
                "between 0 and 1"
            )

        holdings = [
            self._to_holding(position)
            for position in positions
        ]

        cash = capital * cash_percent

        return Portfolio(
            client_name=client_name,
            cash=cash,
            holdings=holdings,
        )

    def _to_holding(
        self,
        position: PEV24ClientPosition,
    ) -> Holding:
        if position is None:
            raise ValueError(
                "position must not be None"
            )

        symbol = str(position.symbol).strip().upper()
        quantity = float(position.quantity)
        average_cost = float(position.average_cost)

        if not symbol:
            raise ValueError(
                "position symbol must not be empty"
            )

        if quantity <= 0:
            raise ValueError(
                f"position quantity must be greater than 0 "
                f"for symbol {symbol}"
            )

        if average_cost < 0:
            raise ValueError(
                f"position average_cost must not be negative "
                f"for symbol {symbol}"
            )

        return Holding(
            symbol=symbol,
            quantity=quantity,
            average_cost=average_cost,
            current_price=None,
        )