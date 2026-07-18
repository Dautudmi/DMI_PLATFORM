from dmi_core.recommendation.rules import RecommendationRule


def test_recommendation_rule_is_abstract():
    try:
        RecommendationRule()
    except TypeError:
        assert True
    else:
        assert False