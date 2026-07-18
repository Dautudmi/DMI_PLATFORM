from dmi_core.decision import DecisionResult


def test_decision_result_explain_generates_text():
    result = DecisionResult(
        recommendation="BUY",
        confidence=88,
        stars=4,
        summary="Good financial quality.",
        reasons=[
            "Financial score is good.",
            "Valuation is acceptable.",
        ],
        risks=[
            "Margin of safety is not very high.",
        ],
    )

    explanation = result.explain()

    assert "Decision: BUY" in explanation
    assert "Confidence: 88%" in explanation
    assert "Financial score is good." in explanation
    assert "Margin of safety is not very high." in explanation


def test_decision_result_uses_custom_explanation():
    result = DecisionResult(
        recommendation="WATCH",
        confidence=70,
        stars=3,
        summary="Acceptable but not attractive.",
        reasons=[],
        risks=[],
        explanation="Custom explanation.",
    )

    assert result.explain() == "Custom explanation."