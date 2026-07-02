from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MetricDefinition:
    """
    Standard definition of a financial metric.
    """

    code: str

    name: str

    category: str

    unit: str

    formula: str

    description: str

    source: str = "DMI"

    schema_version: str = "2.3"