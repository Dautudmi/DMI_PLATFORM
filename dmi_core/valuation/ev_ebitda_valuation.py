from __future__ import annotations

from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.valuation.base_valuation import BaseValuation
from dmi_core.valuation.valuation_config import ValuationConfig
from dmi_core.valuation.valuation_result import ValuationResult


class EVEBITDAValuation(BaseValuation):
    """
    EV/EBITDA valuation model for DMI Platform.

    Formula:
        Target Enterprise Value
            = EBITDA * Target EV/EBITDA

        Target Equity Value
            = Target Enterprise Value
            - Total Debt
            + Cash

        Intrinsic Value Per Share
            = Target Equity Value
            / Charter Capital
            * 10,000
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
        ebitda = self.income_statement.ebitda
        charter_capital = self.balance_sheet.charter_capital

        if ebitda is None or ebitda <= 0:
            return self._create_na_result(
                current_price=current_price,
                description=(
                    "EBITDA is not available or is not positive."
                ),
            )

        if charter_capital is None or charter_capital <= 0:
            return self._create_na_result(
                current_price=current_price,
                description=(
                    "Charter capital is not available "
                    "or is not positive."
                ),
            )

        total_debt = self.balance_sheet.total_debt
        cash = self.balance_sheet.cash

        if total_debt is None:
            total_debt = 0.0

        if cash is None:
            cash = 0.0

        target_enterprise_value = (
            ebitda
            * self.config.target_ev_ebitda
        )

        target_equity_value = (
            target_enterprise_value
            - total_debt
            + cash
        )

        if target_equity_value <= 0:
            return self._create_na_result(
                current_price=current_price,
                description=(
                    "Calculated target equity value "
                    "is not positive."
                ),
            )

        intrinsic_value = (
            target_equity_value
            / charter_capital
            * 10_000
        )

        upside = None
        downside = None
        margin_of_safety = None
        recommendation = "N/A"

        if current_price is not None and current_price > 0:
            upside = (
                intrinsic_value
                - current_price
            ) / current_price

            downside = (
                (
                    current_price
                    - intrinsic_value
                )
                / current_price
                if current_price > intrinsic_value
                else 0.0
            )

            margin_of_safety = (
                (
                    intrinsic_value
                    - current_price
                )
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
            method="EVEBITDA",
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            description=(
                "EV/EBITDA valuation based on EBITDA, "
                "target EV/EBITDA multiple, debt and cash."
            ),
            source=self.config.source,
            schema_version=self.config.schema_version,
        )

    def _create_na_result(
        self,
        current_price: float | None,
        description: str,
    ) -> ValuationResult:
        """
        Return an unavailable EV/EBITDA valuation result.
        """

        return ValuationResult(
            method="EVEBITDA",
            intrinsic_value=None,
            current_price=current_price,
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="N/A",
            description=description,
            source=self.config.source,
            schema_version=self.config.schema_version,
        )