from dmi_core.decision.decision_policy import DecisionPolicy
from dmi_core.decision.evaluators import RecommendationEvaluator


def test_recommendation_evaluator():

    policy = DecisionPolicy()

    recommendation, stars = RecommendationEvaluator.evaluate(
        score=85,
        margin_of_safety=20,
        policy=policy,
    )

    assert recommendation == "STRONG BUY"
    assert stars == 5

    print(recommendation, stars)


if __name__ == "__main__":
    test_recommendation_evaluator()