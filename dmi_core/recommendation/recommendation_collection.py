from dataclasses import dataclass, field

from dmi_core.recommendation.recommendation import Recommendation


@dataclass(slots=True)
class RecommendationCollection:

    recommendations: list[Recommendation] = field(default_factory=list)

    def add(
        self,
        recommendation: Recommendation,
    ) -> None:
        self.recommendations.append(recommendation)

    def __iter__(self):
        return iter(self.recommendations)

    def __len__(self):
        return len(self.recommendations)