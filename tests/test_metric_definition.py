from dmi_core.models.metric_definition import MetricDefinition


def test_metric_definition():

    metric = MetricDefinition(
        code="ROE",
        name="Return on Equity",
        category="Profitability",
        unit="%",
        formula="Net Profit / Equity",
        description="Measures profitability relative to equity."
    )

    assert metric.code == "ROE"
    assert metric.unit == "%"

    print(metric)


if __name__ == "__main__":
    test_metric_definition()