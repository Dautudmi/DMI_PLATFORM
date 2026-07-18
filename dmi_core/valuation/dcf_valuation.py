from __future__ import annotations

from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.valuation.base_valuation import (
    BaseValuation,
)
from dmi_core.valuation.dcf_projection import (
    DCFProjection,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


class DCFValuation(BaseValuation):
    """
    Discounted Cash Flow valuation model.

    Flow:

        Base Free Cash Flow
                ↓
        DCFProjection
                ↓
        Enterprise Value
                ↓
        Enterprise Value - Debt + Cash
                ↓
        Equity Fair Value
                ↓
        Fair Value Per Share

    Formula:

        Equity Value
            = Enterprise Value
            - Total Debt
            + Cash

        Fair Value Per Share
            = Equity Value
            / Charter Capital
            × Par Value

    Assumptions:

    - Financial-statement monetary values use the same unit,
      normally billion VND.
    - Vietnamese listed shares normally have a par value
      of 10,000 VND.
    - Default explicit projection period is 5 years.
    - Default annual free-cash-flow growth is 10%.
    """

    DEFAULT_PAR_VALUE = 10_000.0
    DEFAULT_PROJECTION_YEARS = 5
    DEFAULT_GROWTH_RATE = 0.10

    def __init__(
        self,
        statement: FinancialStatement,
        config: ValuationConfig | None = None,
        projection: DCFProjection | None = None,
        growth_rate: float = DEFAULT_GROWTH_RATE,
        projection_years: int = DEFAULT_PROJECTION_YEARS,
    ) -> None:
        super().__init__(
            statement
        )

        self.config = (
            config
            if config is not None
            else ValuationConfig()
        )

        self.projection = (
            projection
            if projection is not None
            else DCFProjection()
        )

        self.growth_rate = self._validate_growth_rate(
            growth_rate
        )

        self.projection_years = (
            self._validate_projection_years(
                projection_years
            )
        )

    def evaluate(
        self,
        current_price: float | None = None,
    ) -> ValuationResult:
        """
        Calculate DCF fair value per share.
        """

        intrinsic_value = (
            self._calculate_intrinsic_value()
        )

        if intrinsic_value is None:
            return self._create_na_result(
                current_price=current_price,
            )

        (
            upside,
            downside,
            margin_of_safety,
            recommendation,
        ) = self._calculate_market_metrics(
            intrinsic_value=intrinsic_value,
            current_price=current_price,
        )

        return ValuationResult(
            method="DCF",
            intrinsic_value=intrinsic_value,
            current_price=current_price,
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            description=(
                "DCF valuation based on projected free cash "
                "flows, terminal value and net debt."
            ),
            source=self.config.source,
            schema_version=self.config.schema_version,
        )

    def _calculate_intrinsic_value(
        self,
    ) -> float | None:
        """
        Calculate DCF fair value per share.
        """

        free_cash_flow = getattr(
            self.statement,
            "free_cash_flow",
            None,
        )

        if free_cash_flow is None:
            return None

        if self.balance_sheet is None:
            return None

        charter_capital = (
            self.balance_sheet.charter_capital
        )

        if (
            charter_capital is None
            or charter_capital <= 0
        ):
            return None

        if not self._has_valid_discount_assumptions():
            return None

        projection_result = self.projection.project(
            free_cash_flow=free_cash_flow,
            growth_rate=self.growth_rate,
            discount_rate=self.config.discount_rate,
            terminal_growth_rate=(
                self.config.terminal_growth_rate
            ),
            projection_years=self.projection_years,
        )

        enterprise_value = (
            projection_result.enterprise_value
        )

        if (
            enterprise_value is None
            or enterprise_value <= 0
        ):
            return None

        total_debt = (
            self.balance_sheet.total_debt
        )

        cash = self.balance_sheet.cash

        if total_debt is None:
            total_debt = 0.0

        if cash is None:
            cash = 0.0

        equity_value = (
            enterprise_value
            - total_debt
            + cash
        )

        if equity_value <= 0:
            return None

        intrinsic_value = (
            equity_value
            / charter_capital
            * self.DEFAULT_PAR_VALUE
        )

        if intrinsic_value <= 0:
            return None

        return intrinsic_value

    def _calculate_market_metrics(
        self,
        intrinsic_value: float,
        current_price: float | None,
    ) -> tuple[
        float | None,
        float | None,
        float | None,
        str,
    ]:
        """
        Calculate upside, downside, Margin of Safety
        and valuation recommendation.
        """

        upside = None
        downside = None
        margin_of_safety = None
        recommendation = "N/A"

        if (
            current_price is None
            or current_price <= 0
        ):
            return (
                upside,
                downside,
                margin_of_safety,
                recommendation,
            )

        upside = (
            intrinsic_value - current_price
        ) / current_price

        downside = (
            (
                current_price - intrinsic_value
            )
            / current_price
            if current_price > intrinsic_value
            else 0.0
        )

        margin_of_safety = (
            intrinsic_value - current_price
        ) / intrinsic_value

        if (
            margin_of_safety
            >= self.config.required_margin_of_safety
        ):
            recommendation = "BUY"

        elif margin_of_safety >= 0:
            recommendation = "WATCH"

        else:
            recommendation = "AVOID"

        return (
            upside,
            downside,
            margin_of_safety,
            recommendation,
        )

    def _create_na_result(
        self,
        current_price: float | None,
    ) -> ValuationResult:
        """
        Return a standardized unavailable DCF result.
        """

        return ValuationResult(
            method="DCF",
            intrinsic_value=None,
            current_price=current_price,
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="N/A",
            description=(
                "DCF valuation cannot be calculated because "
                "free cash flow, capital structure or discount "
                "assumptions are incomplete."
            ),
            source=self.config.source,
            schema_version=self.config.schema_version,
        )

    def _has_valid_discount_assumptions(
        self,
    ) -> bool:
        """
        Validate the Gordon Growth assumptions.

        Discount rate must be greater than terminal growth rate.
        """

        discount_rate = self.config.discount_rate

        terminal_growth_rate = (
            self.config.terminal_growth_rate
        )

        if discount_rate <= 0:
            return False

        if terminal_growth_rate <= -1:
            return False

        if (
            discount_rate
            <= terminal_growth_rate
        ):
            return False

        return True

    def _validate_growth_rate(
        self,
        growth_rate: float,
    ) -> float:
        if isinstance(
            growth_rate,
            bool,
        ):
            raise TypeError(
                "growth_rate must be numeric"
            )

        if not isinstance(
            growth_rate,
            (int, float),
        ):
            raise TypeError(
                "growth_rate must be numeric"
            )

        numeric_growth_rate = float(
            growth_rate
        )

        if numeric_growth_rate <= -1:
            raise ValueError(
                "growth_rate must be greater than -1"
            )

        return numeric_growth_rate

    def _validate_projection_years(
        self,
        projection_years: int,
    ) -> int:
        if isinstance(
            projection_years,
            bool,
        ):
            raise TypeError(
                "projection_years must be an integer"
            )

        if not isinstance(
            projection_years,
            int,
        ):
            raise TypeError(
                "projection_years must be an integer"
            )

        if projection_years <= 0:
            raise ValueError(
                "projection_years must be greater than zero"
            )

        return projection_years