from dmi_core.insights import (
    Evidence,
    Insight,
    InsightCategory,
    InsightCollection,
    InsightConfidence,
    InsightSeverity,
)


def test_insight_model():
    insight = Insight(
        category=InsightCategory.ALLOCATION,
        title="High concentration",
        message="Portfolio is highly concentrated in one sector.",
        severity=InsightSeverity.WARNING,
        confidence=InsightConfidence.HIGH,
        evidence=[
            Evidence(
                label="Technology exposure",
                value=48,
                unit="%",
            )
        ],
        suggested_action="Reduce exposure.",
    )

    assert insight.category == InsightCategory.ALLOCATION
    assert insight.severity == InsightSeverity.WARNING
    assert insight.confidence == InsightConfidence.HIGH
    assert insight.evidence[0].value == 48
    assert insight.suggested_action == "Reduce exposure."


def test_insight_collection_adds_insight():
    collection = InsightCollection()

    insight = Insight(
        category=InsightCategory.RISK,
        title="High risk",
        message="Portfolio risk is elevated.",
        severity=InsightSeverity.CRITICAL,
    )

    collection.add(insight)

    assert len(collection) == 1
    assert collection.has_critical() is True


def test_insight_collection_filters_by_severity():
    collection = InsightCollection()

    info = Insight(
        category=InsightCategory.CASH,
        title="Cash allocation",
        message="Cash allocation is normal.",
        severity=InsightSeverity.INFO,
    )

    warning = Insight(
        category=InsightCategory.ALLOCATION,
        title="Sector concentration",
        message="Sector exposure is high.",
        severity=InsightSeverity.WARNING,
    )

    collection.add(info)
    collection.add(warning)

    warnings = collection.by_severity(InsightSeverity.WARNING)

    assert len(warnings) == 1
    assert warnings[0].title == "Sector concentration"