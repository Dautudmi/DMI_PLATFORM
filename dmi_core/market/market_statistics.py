from __future__ import annotations

from dmi_core.market.market_data import (
    MarketData,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)


class MarketStatistics:
    """
    Utility class for deriving market statistics.

    Responsibility

    - infer missing market values
    - calculate shares outstanding
    - calculate market capitalization
    - calculate enterprise value

    This class never downloads data.

    It only derives values from existing
    MarketData + FinancialStatement.
    """

    PAR_VALUE = 10_000.0

    @classmethod
    def enrich(
        cls,
        market: MarketData,
        statement: FinancialStatement | None = None,
    ) -> MarketData:

        if market is None:
            raise ValueError(
                "market must not be None"
            )

        if (
            market.market_cap is None
            and market.current_price is not None
            and market.shares_outstanding is not None
        ):
            market.market_cap = (
                market.current_price
                * market.shares_outstanding
            )

        if (
            market.shares_outstanding is None
            and market.market_cap is not None
            and market.current_price
            and market.current_price > 0
        ):
            market.shares_outstanding = (
                market.market_cap
                / market.current_price
            )

        if (
            statement is not None
            and market.shares_outstanding is None
        ):
            balance = statement.balance_sheet

            if (
                balance is not None
                and balance.charter_capital
                and balance.charter_capital > 0
            ):
                market.shares_outstanding = (
                    balance.charter_capital
                    * 1_000_000_000
                    / cls.PAR_VALUE
                )

        if (
            statement is not None
            and market.enterprise_value is None
            and market.market_cap is not None
        ):
            balance = statement.balance_sheet

            debt = (
                balance.total_debt
                if balance
                and balance.total_debt is not None
                else 0.0
            )

            cash = (
                balance.cash
                if balance
                and balance.cash is not None
                else 0.0
            )

            market.enterprise_value = (
                market.market_cap
                + debt
                - cash
            )

        return market

    @classmethod
    def calculate_eps(
        cls,
        statement: FinancialStatement,
        market: MarketData,
    ) -> float | None:

        if statement is None:
            return None

        income = statement.income_statement

        if income is None:
            return None

        if income.net_profit is None:
            return None

        if (
            market.shares_outstanding is None
            or market.shares_outstanding <= 0
        ):
            return None

        return (
            income.net_profit
            * 1_000_000_000
            / market.shares_outstanding
        )

    @classmethod
    def calculate_bvps(
        cls,
        statement: FinancialStatement,
        market: MarketData,
    ) -> float | None:

        if statement is None:
            return None

        balance = statement.balance_sheet

        if balance is None:
            return None

        if balance.equity is None:
            return None

        if (
            market.shares_outstanding is None
            or market.shares_outstanding <= 0
        ):
            return None

        return (
            balance.equity
            * 1_000_000_000
            / market.shares_outstanding
        )

    @classmethod
    def calculate_pe(
        cls,
        market: MarketData,
        eps: float | None,
    ) -> float | None:

        if (
            eps is None
            or eps <= 0
        ):
            return None

        if (
            market.current_price is None
            or market.current_price <= 0
        ):
            return None

        return (
            market.current_price
            / eps
        )

    @classmethod
    def calculate_pb(
        cls,
        market: MarketData,
        bvps: float | None,
    ) -> float | None:

        if (
            bvps is None
            or bvps <= 0
        ):
            return None

        if (
            market.current_price is None
            or market.current_price <= 0
        ):
            return None

        return (
            market.current_price
            / bvps
        )