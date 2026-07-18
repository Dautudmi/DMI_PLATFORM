from dataclasses import dataclass

from dmi_core.health.health_level import HealthLevel


@dataclass(slots=True)
class PortfolioHealth:
    """
    Overall portfolio health.
    """

    score: int
    level: HealthLevel

    @property
    def healthy(self) -> bool:
        return self.score >= 70