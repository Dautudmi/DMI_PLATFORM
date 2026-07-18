from dmi_core.health import HealthLevel, PortfolioHealth
from dmi_core.insights import (
    Insight,
    InsightCategory,
    InsightCollection,
    InsightSeverity,
)
from dmi_core.metrics import PortfolioMetrics


class PortfolioInsightGenerator:
    """
    Generate business insights from portfolio metrics and health.

    This class never calculates metrics.
    This class never evaluates policies.
    """

    def generate(
        self,
        metrics: PortfolioMetrics,
        health: PortfolioHealth,
    ) -> InsightCollection:

        collection = InsightCollection()

        # Cash

        if metrics.cash_weight < 0.05:

            collection.add(
                Insight(
                    category=InsightCategory.CASH,
                    title="Low Cash Allocation",
                    message="Cash allocation is below the preferred level.",
                    severity=InsightSeverity.WARNING,
                    suggested_action="Increase cash allocation.",
                )
            )

        elif metrics.cash_weight > 0.30:

            collection.add(
                Insight(
                    category=InsightCategory.CASH,
                    title="High Cash Allocation",
                    message="Cash allocation is higher than expected.",
                    severity=InsightSeverity.INFO,
                    suggested_action="Consider deploying available cash.",
                )
            )

        # Concentration

        if metrics.largest_position_weight > 0.30:

            collection.add(
                Insight(
                    category=InsightCategory.PORTFOLIO,
                    title="Large Position",
                    message="One position dominates the portfolio.",
                    severity=InsightSeverity.WARNING,
                    suggested_action="Reduce concentration risk.",
                )
            )

        # Portfolio Health

        if health.level in (
            HealthLevel.WEAK,
            HealthLevel.CRITICAL,
        ):

            collection.add(
                Insight(
                    category=InsightCategory.PORTFOLIO,
                    title="Portfolio Health",
                    message="Overall portfolio health requires attention.",
                    severity=InsightSeverity.CRITICAL,
                    suggested_action="Review the portfolio.",
                )
            )

        elif health.level == HealthLevel.EXCELLENT:

            collection.add(
                Insight(
                    category=InsightCategory.PORTFOLIO,
                    title="Healthy Portfolio",
                    message="Portfolio is in excellent condition.",
                    severity=InsightSeverity.INFO,
                )
            )

        return collection