from dataclasses import dataclass, field

from dmi_core.insights.enums import InsightSeverity
from dmi_core.insights.insight import Insight


@dataclass(slots=True)
class InsightCollection:
    """
    Collection of insights.
    """

    insights: list[Insight] = field(default_factory=list)

    def add(self, insight: Insight) -> None:
        self.insights.append(insight)

    def by_severity(self, severity: InsightSeverity) -> list[Insight]:
        return [
            insight
            for insight in self.insights
            if insight.severity == severity
        ]

    def has_critical(self) -> bool:
        return len(self.by_severity(InsightSeverity.CRITICAL)) > 0

    def __len__(self) -> int:
        return len(self.insights)