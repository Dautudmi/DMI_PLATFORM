from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.valuation.base_valuation import BaseValuation
from dmi_core.valuation.valuation_config import ValuationConfig
from dmi_core.valuation.valuation_result import ValuationResult


class PBValuation(BaseValuation):
    """
    Price / Book valuation.

    BVPS = Equity / Charter Capital * 10,000
    Fair Value = BVPS * Target PB
    """

    def __init__(
        self,
        statement: FinancialStatement,
        config: ValuationConfig | None = None,
    ):
        super().__init__(statement)
        self.config = config or ValuationConfig()

    def evaluate(
        self,
        current_price: float | None = None,
    ) -> ValuationResult:

        equity = self.balance_sheet.equity
        charter_capital = self.balance_sheet.charter_capital

        if (
            equity is None
            or equity <= 0
            or charter_capital is None
            or charter_capital <= 0
        ):
            return ValuationResult(
                method="PB",
                intrinsic_value=None,
                current_price=current_price,
                upside=None,
                downside=None,
                margin_of_safety=None,
                recommendation="N/A",
                description="Book value is not available.",
                source=self.config.source,
                schema_version=self.config.schema_version,
            )

        # BVPS (mệnh giá 10.000)
        bvps = equity / charter_capital * 10_000

        intrinsic_value = (
            bvps
            * self.config.target_pb
        )

        upside = None
        downside = None
        margin_of_safety = None
        recommendation = "N/A"

        if current_price is not None and current_price > 0:

            upside = (
                intrinsic_value - current_price
            ) / current_price

            downside = (
                (current_price - intrinsic_value)
                / current_price
                if current_price > intrinsic_value
                else 0.0
            )

            margin_of_safety = (
                (intrinsic_value - current_price)
                / intrinsic_value
                if intrinsic_value > 0
                else None
            )

            if margin_of_safety is not None:
                if (
                    margin_of_safety
                    >= self.config.required_margin_of_safety
                ):
                    recommendation = "BUY"
                elif margin_of_safety >= 0:
                    recommendation = "WATCH"
                else:
                    recommendation = "AVOID"

        return ValuationResult(
            method="PB",
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            description="P/B valuation based on book value per share.",
            source=self.config.source,
            schema_version=self.config.schema_version,
        )