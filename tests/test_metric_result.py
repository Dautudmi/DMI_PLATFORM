from dmi_core.models.metric_result import MetricResult


def test_metric_result():

    result = MetricResult(
        code="ROE",
        name="Return on Equity",
        value=0.026,
        display="2.60%",
        unit="%",
        formula="Net Profit / Equity",
        description="Return on Equity",
    )

    assert result.code == "ROE"
    assert result.value == 0.026
    assert result.display == "2.60%"
    assert result.unit == "%"

    print(result)


if __name__ == "__main__":
    test_metric_result()