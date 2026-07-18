from dataclasses import dataclass, field

from dmi_core.insights import Insight
from dmi_core.reasoning.conflict import Conflict
from dmi_core.reasoning.priority_group import PriorityGroup


@dataclass(slots=True)
class RecommendationContext:
    """
    Context prepared by Reasoning Engine for Recommendation Engine.

    This is not a final recommendation.
    """

    insights: list[Insight] = field(default_factory=list)
    priority_groups: list[PriorityGroup] = field(default_factory=list)
    conflicts: list[Conflict] = field(default_factory=list)
    summary: str | None = None