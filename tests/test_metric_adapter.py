from dmi_core.metrics import MetricAdapter


def test_metric_adapter():

    adapter = MetricAdapter()

    result = adapter.build_result(
        code="ROE",
        value=0.15,
        display="15.00%",
    )

    assert result.code == "ROE"
    assert result.name == "Return on Equity"
    assert result.unit == "%"
    assert result.display == "15.00%"

    print(result)


if __name__ == "__main__":
    test_metric_adapter()