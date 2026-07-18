from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Evidence:
    """
    Supporting evidence for an insight.
    """

    label: str
    value: Any
    unit: str | None = None