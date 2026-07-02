from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ValuationResult:
    """
    Standard valuation result for DMI Platform.
    """

    method: str

    intrinsic_value: Optional[float]

    current_price: Optional[float]

    upside: Optional[float]

    downside: Optional[float]

    margin_of_safety: Optional[float]

    recommendation: str

    description: Optional[str] = None

    source: str = "DMI"

    schema_version: str = "3.0"