from dataclasses import dataclass, field

from dmi_core.insights import Insight


@dataclass(slots=True)
class PriorityGroup:
    """
    A group of insights with the same reasoning priority.
    """

    priority: int
    title: str
    insights: list[Insight] = field(default_factory=list)