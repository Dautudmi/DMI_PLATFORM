from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PipelineContext:
    """
    Base context passed through pipeline stages.
    """

    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)