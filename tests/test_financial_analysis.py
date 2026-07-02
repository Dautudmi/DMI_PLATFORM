from dmi_core.analysis import FinancialAnalysis
from dmi_core.services import FinancialStatementService


def test_financial_analysis():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    analysis = FinancialAnalysis(statement)

    profitability = analysis.profitability()
    leverage = analysis.leverage()
    result = analysis.analyze()

    assert profitability.code == "PROFITABILITY"
    assert leverage.code == "LEVERAGE"

    assert result.profitability is not None
    assert result.leverage is not None
    assert result.overall_score > 0
    assert result.overall_rating in ["A", "B", "C", "D", "E"]

    print("=" * 60)
    print("DMI FINANCIAL ANALYSIS")
    print("=" * 60)

    print("PROFITABILITY")
    print("Rating         :", profitability.rating)
    print("Score          :", profitability.score)
    print("Summary        :", profitability.summary)
    print("Recommendation :", profitability.recommendation)

    print("-" * 60)

    print("LEVERAGE")
    print("Rating         :", leverage.rating)
    print("Score          :", leverage.score)
    print("Summary        :", leverage.summary)
    print("Recommendation :", leverage.recommendation)

    print("-" * 60)

    print("OVERALL")
    print("Score          :", result.overall_score)
    print("Rating         :", result.overall_rating)
    print("Recommendation :", result.recommendation)

    print("=" * 60)


if __name__ == "__main__":
    test_financial_analysis()