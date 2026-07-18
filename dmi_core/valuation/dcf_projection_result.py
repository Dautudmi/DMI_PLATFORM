from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DCFProjectionResult:
    """
    Result of a discounted cash flow projection.

    This object contains only projection outputs.

    It intentionally does not perform valuation or
    investment recommendation.
    """

    projected_cash_flows: list[float] = field(
        default_factory=list
    )

    terminal_value: float | None = None

    present_value_cash_flows: list[float] = field(
        default_factory=list
    )

    present_value_terminal: float | None = None

    enterprise_value: float | None = None

    projection_years: int = 5

    growth_rate: float = 0.10

    discount_rate: float = 0.12

    terminal_growth_rate: float = 0.03

    source: str = "DMI"

    schema_version: str = "1.0"

    @property
    def total_present_value(self) -> float | None:
        """
        Enterprise Value after discounting.
        """
        return self.enterprise_value

    @property
    def is_valid(self) -> bool:
        return self.enterprise_value is not None

    def explain(self) -> str:
        if not self.is_valid:
            return "Invalid DCF projection."

        return (
            f"DCF Projection\n"
            f"Years: {self.projection_years}\n"
            f"Enterprise Value: "
            f"{self.enterprise_value:,.2f}"
        )