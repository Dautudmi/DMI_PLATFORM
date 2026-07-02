from dmi_core.rules import LeverageRules


def test_leverage_rules():

    result = LeverageRules.evaluate(debt_to_equity=1.2)

    assert result.code == "LEVERAGE"
    assert result.rating == "Average"
    assert result.score == 60

    print(result)


if __name__ == "__main__":
    test_leverage_rules()