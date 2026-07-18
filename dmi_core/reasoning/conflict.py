from dataclasses import dataclass

from dmi_core.insights import Insight


@dataclass(slots=True)
class Conflict:
    """
    Represents conflicting insights.
    """

    title: str
    description: str
    insights: list[Insight]