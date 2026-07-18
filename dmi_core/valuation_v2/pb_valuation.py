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


class PBValuationV2(
    BaseValuationV2
):
    """
    Price / Book valuation model V2.

    V2 sử dụng:

        FinancialStatement
                +
            MarketData

    BVPS resolution priority:

    1. balance_sheet.book_value_per_share
    2. balance_sheet.bvps
    3. equity / shares_outstanding

    Intrinsic Value:

        BVPS × Target P/B
    """

    method = "PB"

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

        bvps = self._resolve_bvps(
            statement=statement,
            market=market,
        )

        if bvps is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Unable to determine book value "
                    "per share."
                ),
            )

        target_pb = self.positive_or_none(
            self.config.target_pb
        )

        if target_pb is None:
            return self.create_unavailable_result(
                current_price=market.current_price,
                description=(
                    "Target P/B must be greater than zero."
                ),
            )

        intrinsic_value = (
            bvps
            * target_pb
        )

        return self.create_result(
            intrinsic_value=intrinsic_value,
            current_price=market.current_price,
            description=(
                "P/B valuation completed. "
                f"BVPS={bvps:.4f}, "
                f"Target P/B={target_pb:.4f}."
            ),
        )

    def _resolve_bvps(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> float | None:
        """
        Resolve BVPS using direct and derived values.

        Priority:

        1. balance_sheet.book_value_per_share
        2. balance_sheet.bvps
        3. MarketStatistics.calculate_bvps(...)
        """

        balance_sheet = (
            statement.balance_sheet
        )

        if balance_sheet is not None:
            direct_book_value_per_share = (
                self.positive_or_none(
                    getattr(
                        balance_sheet,
                        "book_value_per_share",
                        None,
                    )
                )
            )

            if (
                direct_book_value_per_share
                is not None
            ):
                return (
                    direct_book_value_per_share
                )

            direct_bvps = self.positive_or_none(
                getattr(
                    balance_sheet,
                    "bvps",
                    None,
                )
            )

            if direct_bvps is not None:
                return direct_bvps

        derived_bvps = (
            MarketStatistics.calculate_bvps(
                statement=statement,
                market=market,
            )
        )

        return self.positive_or_none(
            derived_bvps
        )