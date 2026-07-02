from dmi_core.dictionary import MetricRegistry


def test_metric_registry():

    registry = MetricRegistry()

    roe = registry.get("ROE")
    profitability = registry.by_category("Profitability")

    assert registry.exists("ROE")
    assert roe is not None
    assert roe.name == "Return on Equity"
    assert len(profitability) > 0

    print("=" * 60)
    print("DMI METRIC REGISTRY")
    print("=" * 60)

    print("ROE:", roe)

    print("-" * 60)
    print("PROFITABILITY METRICS")

    for metric in profitability:
        print(
            f"{metric.code:<18}"
            f"{metric.name:<30}"
            f"{metric.unit}"
        )

    print("-" * 60)
    print("ALL CODES")
    print(registry.codes())

    print("=" * 60)


if __name__ == "__main__":
    test_metric_registry()