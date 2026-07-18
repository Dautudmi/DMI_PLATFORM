from dmi_core.health import HealthLevel, PortfolioHealth
from dmi_core.metrics import PortfolioMetrics
from dmi_core.policies import PortfolioPolicy


class PortfolioHealthEvaluator:
    """
    Evaluate portfolio health from objective metrics and policy.

    Metrics are facts.
    Health is policy-dependent.
    """

    def evaluate(
        self,
        metrics: PortfolioMetrics,
        policy: PortfolioPolicy | None = None,
    ) -> PortfolioHealth:
        policy = policy or PortfolioPolicy.balanced()

        score = 100

        if metrics.total_value <= 0:
            return PortfolioHealth(
                score=0,
                level=HealthLevel.CRITICAL,
            )

        if metrics.cash_weight < policy.min_cash:
            score -= 20

        if metrics.cash_weight > policy.max_cash:
            score -= 15

        if metrics.largest_position_weight > policy.max_single_position:
            score -= 25

        if metrics.concentration_ratio > policy.max_sector_weight:
            score -= 20

        score = max(0, min(100, score))

        return PortfolioHealth(
            score=score,
            level=self._level_from_score(score),
        )

    def _level_from_score(
        self,
        score: int,
    ) -> HealthLevel:
        if score >= 90:
            return HealthLevel.EXCELLENT

        if score >= 75:
            return HealthLevel.GOOD

        if score >= 60:
            return HealthLevel.FAIR

        if score >= 40:
            return HealthLevel.WEAK

        return HealthLevel.CRITICAL