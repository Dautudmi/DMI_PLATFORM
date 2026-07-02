from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.valuation.base_valuation import BaseValuation
from dmi_core.valuation.valuation_config import ValuationConfig
from dmi_core.valuation.valuation_result import ValuationResult


class PEValuation(BaseValuation):
    """
    P/E valuation model for DMI Platform.

    Formula:
        Intrinsic Value = EPS * Target P/E
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
        eps = self.income_statement.eps

        if eps is None:
            return ValuationResult(
                method="PE",
                intrinsic_value=None,
                current_price=current_price,
                upside=None,
                downside=None,
                margin_of_safety=None,
                recommendation="N/A",
                description="EPS is not available.",
            )

        intrinsic_value = eps * self.config.target_pe

        upside = None
        downside = None
        margin_of_safety = None
        recommendation = "N/A"

        if current_price is not None and current_price > 0:
            upside = (intrinsic_value - current_price) / current_price

            downside = (
                (current_price - intrinsic_value) / current_price
                if current_price > intrinsic_value
                else 0
            )

            margin_of_safety = (
                (intrinsic_value - current_price) / intrinsic_value
                if intrinsic_value > 0
                else None
            )

            if margin_of_safety is not None:
                if margin_of_safety >= self.config.required_margin_of_safety:
                    recommendation = "BUY"
                elif margin_of_safety >= 0:
                    recommendation = "WATCH"
                else:
                    recommendation = "AVOID"

        return ValuationResult(
            method="PE",
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            description="P/E valuation based on EPS and target P/E.",
        )