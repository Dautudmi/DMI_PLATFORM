from dmi_core.rules import ProfitabilityRules


def test_profitability_rules():

    result = ProfitabilityRules.evaluate(roe=0.18)

    assert result.code == "PROFITABILITY"
    assert result.rating == "Good"
    assert result.score == 80

    print(result)


if __name__ == "__main__":
    test_profitability_rules()