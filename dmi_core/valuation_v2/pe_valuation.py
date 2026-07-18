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


class PEValuationV2(
    BaseValuationV2
):
    """
    Price / Earnings valuation model V2.

    V2 sử dụng:

        FinancialStatement
                +
            MarketData

    EPS resolution priority:

    1. income_statement.eps
    2. net_profit / shares_outstanding

    Intrinsic Value:

        EPS × Target P/E
    """

    method = "PE"

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

        eps = self._resolve_eps(
            statement=statement,
            market=market,
        )

        if eps is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Unable to determine EPS."
                ),
            )

        target_pe = self.positive_or_none(
            self.config.target_pe
        )

        if target_pe is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Target P/E must be greater than zero."
                ),
            )

        intrinsic_value = (
            eps
            * target_pe
        )

        return self.create_result(
            intrinsic_value=intrinsic_value,
            current_price=market.current_price,
            description=(
                "P/E valuation completed. "
                f"EPS={eps:.4f}, "
                f"Target P/E={target_pe:.4f}."
            ),
        )

    def _resolve_eps(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> float | None:
        """
        Resolve EPS using direct and derived values.

        Priority:

        1. income_statement.eps
        2. MarketStatistics.calculate_eps(...)
        """

        income_statement = (
            statement.income_statement
        )

        if income_statement is not None:
            direct_eps = self.positive_or_none(
                getattr(
                    income_statement,
                    "eps",
                    None,
                )
            )

            if direct_eps is not None:
                return direct_eps

        derived_eps = (
            MarketStatistics.calculate_eps(
                statement=statement,
                market=market,
            )
        )

        return self.positive_or_none(
            derived_eps
        )