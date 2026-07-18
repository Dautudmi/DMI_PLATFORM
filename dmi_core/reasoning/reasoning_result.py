from dataclasses import dataclass

from dmi_core.reasoning.recommendation_context import RecommendationContext


@dataclass(slots=True)
class ReasoningResult:
    """
    Result returned by Reasoning Engine.
    """

    context: RecommendationContext

    @property
    def has_conflicts(self) -> bool:
        return len(self.context.conflicts) > 0