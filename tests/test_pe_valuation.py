from dmi_core.services import FinancialStatementService
from dmi_core.valuation import PEValuation, ValuationConfig


def test_pe_valuation():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    config = ValuationConfig(
        target_pe=10.0,
        required_margin_of_safety=0.25,
    )

    valuation = PEValuation(
        statement=statement,
        config=config,
    )

    result = valuation.evaluate(
        current_price=10.0,
    )

    assert result.method == "PE"

    print("=" * 60)
    print("PE VALUATION")
    print("=" * 60)
    print("Intrinsic Value :", result.intrinsic_value)
    print("Current Price   :", result.current_price)
    print("Upside          :", result.upside)
    print("Margin Safety   :", result.margin_of_safety)
    print("Recommendation  :", result.recommendation)
    print("=" * 60)


if __name__ == "__main__":
    test_pe_valuation()