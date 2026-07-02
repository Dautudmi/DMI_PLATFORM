from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class MetricResult:
    """
    DMI Standard Metric Result.

    This model represents the result of a financial metric calculation.
    It contains both raw value and display-ready value.
    """

    code: str
    name: str

    value: Optional[float]
    display: str
    unit: str

    formula: Optional[str] = None
    description: Optional[str] = None
    source: str = "DMI"
    schema_version: str = "2.1"