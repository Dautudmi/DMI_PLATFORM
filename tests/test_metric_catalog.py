from dmi_core.dictionary.metric_catalog import ALL_METRICS


def test_metric_catalog():

    assert len(ALL_METRICS) >= 10

    print("=" * 60)
    print("DMI METRIC CATALOG")
    print("=" * 60)

    for metric in ALL_METRICS:
        print(
            f"{metric.code:<18}"
            f"{metric.category:<18}"
            f"{metric.unit:<10}"
            f"{metric.name}"
        )

    print("=" * 60)


if __name__ == "__main__":
    test_metric_catalog()