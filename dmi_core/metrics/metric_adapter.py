from dmi_core.dictionary import MetricRegistry
from dmi_core.models.metric_definition import MetricDefinition
from dmi_core.models.metric_result import MetricResult


class MetricAdapter:
    """
    Adapter between MetricRegistry and MetricResult.

    This class helps FinancialMetrics attach metadata from MetricRegistry
    to calculated metric values.
    """

    def __init__(self):
        self.registry = MetricRegistry()

    def build_result(
        self,
        code: str,
        value: float | None,
        display: str,
    ) -> MetricResult:
        definition: MetricDefinition | None = self.registry.get(code)

        if definition is None:
            return MetricResult(
                code=code,
                name=code,
                value=value,
                display=display,
                unit="",
                formula=None,
                description=None,
            )

        return MetricResult(
            code=definition.code,
            name=definition.name,
            value=value,
            display=display,
            unit=definition.unit,
            formula=definition.formula,
            description=definition.description,
        )