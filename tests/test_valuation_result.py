from dmi_core.valuation.valuation_result import ValuationResult


def test_valuation_result():

    result = ValuationResult(
        method="PE",
        intrinsic_value=42.5,
        current_price=35.0,
        upside=21.4,
        downside=0.0,
        margin_of_safety=17.6,
        recommendation="BUY",
    )

    assert result.method == "PE"
    assert result.intrinsic_value == 42.5
    assert result.recommendation == "BUY"

    print(result)


if __name__ == "__main__":
    test_valuation_result()