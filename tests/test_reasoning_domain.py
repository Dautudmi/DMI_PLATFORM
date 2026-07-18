from dmi_core.insights import (
    Insight,
    InsightCategory,
    InsightSeverity,
)
from dmi_core.reasoning import (
    Conflict,
    PriorityGroup,
    RecommendationContext,
    ReasoningResult,
)


def test_priority_group_model():
    insight = Insight(
        category=InsightCategory.RISK,
        title="High risk",
        message="Portfolio risk is elevated.",
        severity=InsightSeverity.WARNING,
    )

    group = PriorityGroup(
        priority=1,
        title="Risk concerns",
        insights=[insight],
    )

    assert group.priority == 1
    assert group.title == "Risk concerns"
    assert group.insights[0].title == "High risk"


def test_conflict_model():
    insight_a = Insight(
        category=InsightCategory.ALLOCATION,
        title="Increase banking",
        message="Banking allocation can be increased.",
    )

    insight_b = Insight(
        category=InsightCategory.RISK,
        title="Reduce banking",
        message="Banking risk is elevated.",
        severity=InsightSeverity.WARNING,
    )

    conflict = Conflict(
        title="Banking allocation conflict",
        description="Allocation and risk insights are conflicting.",
        insights=[insight_a, insight_b],
    )

    assert conflict.title == "Banking allocation conflict"
    assert len(conflict.insights) == 2


def test_recommendation_context_model():
    insight = Insight(
        category=InsightCategory.CASH,
        title="High cash",
        message="Cash allocation is high.",
    )

    group = PriorityGroup(
        priority=1,
        title="Cash management",
        insights=[insight],
    )

    context = RecommendationContext(
        insights=[insight],
        priority_groups=[group],
        summary="Portfolio has high cash allocation.",
    )

    assert len(context.insights) == 1
    assert len(context.priority_groups) == 1
    assert context.summary == "Portfolio has high cash allocation."


def test_reasoning_result_detects_conflicts():
    insight_a = Insight(
        category=InsightCategory.ALLOCATION,
        title="Increase banking",
        message="Increase banking allocation.",
    )

    insight_b = Insight(
        category=InsightCategory.RISK,
        title="Reduce banking",
        message="Reduce banking allocation.",
        severity=InsightSeverity.WARNING,
    )

    conflict = Conflict(
        title="Banking conflict",
        description="Conflicting banking insights.",
        insights=[insight_a, insight_b],
    )

    context = RecommendationContext(
        insights=[insight_a, insight_b],
        conflicts=[conflict],
    )

    result = ReasoningResult(context=context)

    assert result.has_conflicts is True