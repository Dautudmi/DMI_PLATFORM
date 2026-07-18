from dataclasses import dataclass, field


@dataclass(slots=True)
class HealthSummary:
    """
    Human-readable portfolio health summary.
    """

    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)