from __future__ import annotations

from dmi_core.models.free_cash_flow import (
    FreeCashFlow,
)
from dmi_core.valuation.dcf_projection_result import (
    DCFProjectionResult,
)


class DCFProjection:
    """
    Cash-flow projection engine.

    Responsibility:

    - project future FCF
    - calculate terminal value
    - discount future cash flows

    This class intentionally does NOT calculate
    intrinsic value per share.
    """

    def project(
        self,
        free_cash_flow: FreeCashFlow,
        *,
        growth_rate: float,
        discount_rate: float,
        terminal_growth_rate: float,
        projection_years: int = 5,
    ) -> DCFProjectionResult:

        base_fcf = (
            free_cash_flow.resolved_free_cash_flow()
        )

        if base_fcf is None:
            return DCFProjectionResult()

        projected = []
        discounted = []

        current = base_fcf

        for year in range(1, projection_years + 1):

            current *= (
                1.0 + growth_rate
            )

            projected.append(current)

            discounted.append(
                current
                / (
                    (1.0 + discount_rate)
                    ** year
                )
            )

        terminal_cash_flow = (
            projected[-1]
            * (1.0 + terminal_growth_rate)
        )

        terminal_value = (
            terminal_cash_flow
            / (
                discount_rate
                - terminal_growth_rate
            )
        )

        discounted_terminal = (
            terminal_value
            / (
                (1.0 + discount_rate)
                ** projection_years
            )
        )

        enterprise_value = (
            sum(discounted)
            + discounted_terminal
        )

        return DCFProjectionResult(
            projected_cash_flows=projected,
            terminal_value=terminal_value,
            present_value_cash_flows=discounted,
            present_value_terminal=discounted_terminal,
            enterprise_value=enterprise_value,
            projection_years=projection_years,
            growth_rate=growth_rate,
            discount_rate=discount_rate,
            terminal_growth_rate=terminal_growth_rate,
        )