from dmi_core.insights import (
    Evidence,
    Insight,
    InsightCategory,
    InsightConfidence,
    InsightImpact,
    InsightSeverity,
)


def test_insight_v2_fields():
    insight = Insight(
        insight_id="PORT-001",
        category=InsightCategory.PORTFOLIO,
        title="Large Position",
        message="One position dominates the portfolio.",
        severity=InsightSeverity.WARNING,
        confidence=InsightConfidence.HIGH,
        impact=InsightImpact.HIGH,
        source="PortfolioInsightGenerator",
        tags=["portfolio", "concentration"],
        evidence=[
            Evidence(
                label="Largest position weight",
                value=0.45,
                unit="%",
            )
        ],
        suggested_action="Reduce concentration risk.",
    )

    assert insight.insight_id == "PORT-001"
    assert insight.category == InsightCategory.PORTFOLIO
    assert insight.severity == InsightSeverity.WARNING
    assert insight.confidence == InsightConfidence.HIGH
    assert insight.impact == InsightImpact.HIGH
    assert insight.source == "PortfolioInsightGenerator"
    assert "concentration" in insight.tags
    assert insight.evidence[0].label == "Largest position weight"
    assert insight.suggested_action == "Reduce concentration risk."


def test_insight_v2_defaults():
    insight = Insight(
        category=InsightCategory.CASH,
        title="Cash Allocation",
        message="Cash allocation is normal.",
    )

    assert insight.severity == InsightSeverity.INFO
    assert insight.confidence == InsightConfidence.MEDIUM
    assert insight.impact == InsightImpact.MEDIUM
    assert insight.evidence == []
    assert insight.tags == []
    assert insight.source is None
    assert insight.insight_id is None