from abc import ABC, abstractmethod

from dmi_core.portfolio import PortfolioEvaluation
from dmi_core.recommendation import Recommendation


class RecommendationRule(ABC):
    """
    Base class for recommendation rules.

    A rule evaluates PortfolioEvaluation and may return one recommendation.
    """

    @abstractmethod
    def evaluate(
        self,
        evaluation: PortfolioEvaluation,
    ) -> Recommendation | None:
        raise NotImplementedError