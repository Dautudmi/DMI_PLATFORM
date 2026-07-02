from dmi_core.dictionary.metric_catalog import ALL_METRICS
from dmi_core.models.metric_definition import MetricDefinition


class MetricRegistry:
    """
    DMI Metric Registry.

    Provides lookup and filtering for all financial metric definitions.
    """

    def __init__(self):
        self._metrics: dict[str, MetricDefinition] = {
            metric.code: metric
            for metric in ALL_METRICS
        }

    def get(self, code: str) -> MetricDefinition | None:
        """
        Get metric definition by code.
        """

        return self._metrics.get(code)

    def all(self) -> list[MetricDefinition]:
        """
        Return all metric definitions.
        """

        return list(self._metrics.values())

    def codes(self) -> list[str]:
        """
        Return all metric codes.
        """

        return list(self._metrics.keys())

    def by_category(self, category: str) -> list[MetricDefinition]:
        """
        Return all metrics in a category.
        """

        return [
            metric
            for metric in self._metrics.values()
            if metric.category == category
        ]

    def exists(self, code: str) -> bool:
        """
        Check whether a metric code exists.
        """

        return code in self._metrics