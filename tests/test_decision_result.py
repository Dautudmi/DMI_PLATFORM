from dmi_core.decision import DecisionResult


def test_decision_result():

    result = DecisionResult(
        recommendation="BUY",
        confidence=90,
        stars=5,
        summary="Good financial quality with attractive valuation.",
        reasons=["Good financial score."],
        risks=[],
    )

    assert result.recommendation == "BUY"
    assert result.confidence == 90
    assert result.stars == 5
    assert result.summary is not None

    print(result)


if __name__ == "__main__":
    test_decision_result()