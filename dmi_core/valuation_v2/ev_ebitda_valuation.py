from __future__ import annotations

from dmi_core.market.market_data import (
    MarketData,
)
from dmi_core.market.market_statistics import (
    MarketStatistics,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation_v2.base_valuation import (
    BaseValuationV2,
)


class EVEBITDAValuationV2(
    BaseValuationV2
):
    """
    Enterprise Value / EBITDA valuation model V2.

    V2 sử dụng:

        FinancialStatement
                +
            MarketData

    Quy trình:

        EBITDA
            × Target EV/EBITDA
            = Target Enterprise Value

        Target Enterprise Value
            - Net Debt
            = Target Equity Value

        Target Equity Value
            / Shares Outstanding
            = Intrinsic Value Per Share
    """

    method = "EV/EBITDA"

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:
        self.validate_inputs(
            statement=statement,
            market=market,
        )

        MarketStatistics.enrich(
            market=market,
            statement=statement,
        )

        ebitda = self._resolve_ebitda(
            statement=statement,
        )

        if ebitda is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Unable to determine EBITDA."
                ),
            )

        target_ev_ebitda = self.positive_or_none(
            self.config.target_ev_ebitda
        )

        if target_ev_ebitda is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Target EV/EBITDA must be "
                    "greater than zero."
                ),
            )

        shares_outstanding = (
            self.positive_or_none(
                market.shares_outstanding
            )
        )

        if shares_outstanding is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Unable to determine "
                    "shares outstanding."
                ),
            )

        net_debt = self._resolve_net_debt(
            statement=statement,
        )

        target_enterprise_value = (
            ebitda
            * target_ev_ebitda
        )

        target_equity_value = (
            target_enterprise_value
            - net_debt
        )

        if target_equity_value <= 0:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Target equity value is not "
                    "greater than zero after "
                    "subtracting net debt."
                ),
            )

        intrinsic_value = (
            target_equity_value
            * 1_000_000_000
            / shares_outstanding
        )

        return self.create_result(
            intrinsic_value=intrinsic_value,
            current_price=market.current_price,
            description=(
                "EV/EBITDA valuation completed. "
                f"EBITDA={ebitda:.4f}, "
                f"Target EV/EBITDA="
                f"{target_ev_ebitda:.4f}, "
                f"Net Debt={net_debt:.4f}, "
                f"Shares={shares_outstanding:.4f}."
            ),
        )

    def _resolve_ebitda(
        self,
        statement: FinancialStatement,
    ) -> float | None:
        """
        Resolve EBITDA using this priority:

        1. income_statement.ebitda
        2. operating_profit
           + depreciation
           + amortization
        3. EBIT
           + depreciation
           + amortization
        """

        income_statement = (
            statement.income_statement
        )

        if income_statement is None:
            return None

        direct_ebitda = self.positive_or_none(
            getattr(
                income_statement,
                "ebitda",
                None,
            )
        )

        if direct_ebitda is not None:
            return direct_ebitda

        depreciation = (
            self.non_negative_or_zero(
                getattr(
                    income_statement,
                    "depreciation",
                    None,
                )
            )
        )

        amortization = (
            self.non_negative_or_zero(
                getattr(
                    income_statement,
                    "amortization",
                    None,
                )
            )
        )

        operating_profit = (
            self.positive_or_none(
                getattr(
                    income_statement,
                    "operating_profit",
                    None,
                )
            )
        )

        if operating_profit is not None:
            return (
                operating_profit
                + depreciation
                + amortization
            )

        ebit = self.positive_or_none(
            getattr(
                income_statement,
                "ebit",
                None,
            )
        )

        if ebit is not None:
            return (
                ebit
                + depreciation
                + amortization
            )

        return None

    def _resolve_net_debt(
        self,
        statement: FinancialStatement,
    ) -> float:
        """
        Resolve net debt:

            Total Debt - Cash

        Net debt may be negative when the company
        holds net cash. A negative value increases
        target equity value.
        """

        balance_sheet = (
            statement.balance_sheet
        )

        if balance_sheet is None:
            return 0.0

        direct_net_debt = self._number_or_none(
            getattr(
                balance_sheet,
                "net_debt",
                None,
            )
        )

        if direct_net_debt is not None:
            return direct_net_debt

        total_debt = self._resolve_total_debt(
            balance_sheet=balance_sheet,
        )

        cash = self._resolve_cash(
            balance_sheet=balance_sheet,
        )

        return (
            total_debt
            - cash
        )

    def _resolve_total_debt(
        self,
        balance_sheet: object,
    ) -> float:
        """
        Resolve total debt from direct or component fields.
        """

        direct_total_debt = self._number_or_none(
            getattr(
                balance_sheet,
                "total_debt",
                None,
            )
        )

        if direct_total_debt is not None:
            return max(
                direct_total_debt,
                0.0,
            )

        short_term_debt = (
            self.non_negative_or_zero(
                getattr(
                    balance_sheet,
                    "short_term_debt",
                    None,
                )
            )
        )

        long_term_debt = (
            self.non_negative_or_zero(
                getattr(
                    balance_sheet,
                    "long_term_debt",
                    None,
                )
            )
        )

        return (
            short_term_debt
            + long_term_debt
        )

    def _resolve_cash(
        self,
        balance_sheet: object,
    ) -> float:
        """
        Resolve cash and cash equivalents.
        """

        cash_and_equivalents = (
            self._number_or_none(
                getattr(
                    balance_sheet,
                    "cash_and_equivalents",
                    None,
                )
            )
        )

        if cash_and_equivalents is not None:
            return max(
                cash_and_equivalents,
                0.0,
            )

        cash = self._number_or_none(
            getattr(
                balance_sheet,
                "cash",
                None,
            )
        )

        if cash is not None:
            return max(
                cash,
                0.0,
            )

        return 0.0

    @staticmethod
    def _number_or_none(
        value: object,
    ) -> float | None:
        """
        Convert a numeric-like value to float.

        Unlike positive_or_none(), this helper allows
        zero and negative values because net debt may
        legitimately be negative.
        """

        if value is None:
            return None

        try:
            return float(
                value
            )
        except (TypeError, ValueError):
            return None