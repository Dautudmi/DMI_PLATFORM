from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class FreeCashFlow:
    """
    DMI standard cash-flow model.

    This model stores the core cash-flow values used by
    cash-flow-based valuation methods such as:

    - DCF
    - FCFF valuation
    - FCFE valuation

    All monetary values should use the same unit as the
    parent FinancialStatement, normally billion VND.
    """

    symbol: str
    year: int

    quarter: Optional[int] = None
    report_type: Optional[str] = None

    # Cash flow from operations
    operating_cash_flow: Optional[float] = None

    # Capital expenditure
    capex: Optional[float] = None

    # Standard free cash flow
    free_cash_flow: Optional[float] = None

    # Free cash flow to firm
    fcff: Optional[float] = None

    # Free cash flow to equity
    fcfe: Optional[float] = None

    # Optional supporting inputs
    depreciation: Optional[float] = None
    amortization: Optional[float] = None
    change_in_working_capital: Optional[float] = None

    # Metadata
    provider: Optional[str] = "DMI"
    currency: str = "VND"
    unit: str = "Billion"
    schema_version: str = "1.0"

    def calculate_free_cash_flow(
        self,
    ) -> float | None:
        """
        Calculate standard free cash flow:

            Free Cash Flow
                = Operating Cash Flow - Capex

        The calculated value is returned but does not mutate
        the dataclass field.
        """

        if self.operating_cash_flow is None:
            return None

        if self.capex is None:
            return None

        return (
            self.operating_cash_flow
            - self.capex
        )

    def resolved_free_cash_flow(
        self,
    ) -> float | None:
        """
        Return the explicitly provided free cash flow when
        available; otherwise calculate it from operating cash
        flow and capex.
        """

        if self.free_cash_flow is not None:
            return self.free_cash_flow

        return self.calculate_free_cash_flow()

    def resolved_fcff(
        self,
    ) -> float | None:
        """
        Return FCFF when explicitly available.

        This method intentionally does not derive FCFF from
        accounting inputs yet. FCFF derivation will be added
        only when the required inputs are standardized.
        """

        return self.fcff

    def resolved_fcfe(
        self,
    ) -> float | None:
        """
        Return FCFE when explicitly available.

        This method intentionally does not derive FCFE from
        incomplete accounting inputs.
        """

        return self.fcfe