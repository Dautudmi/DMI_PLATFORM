from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class AnalysisResult:
    """
    DMI Standard Analysis Result.

    Represents the interpretation of one financial analysis category.
    """

    code: str
    name: str

    rating: str
    score: float

    summary: str

    recommendation: str

    description: Optional[str] = None

    source: str = "DMI"

    schema_version: str = "2.2"