from dataclasses import dataclass


@dataclass(slots=True)
class ValuationConfig:
    """
    Configuration for valuation models.

    This class stores all configurable assumptions used by
    valuation methods.
    """

    target_pe: float = 10.0

    target_pb: float = 1.5

    target_ev_ebitda: float = 8.0

    discount_rate: float = 0.12

    terminal_growth_rate: float = 0.03

    required_margin_of_safety: float = 0.25

    source: str = "DMI"

    schema_version: str = "3.0"