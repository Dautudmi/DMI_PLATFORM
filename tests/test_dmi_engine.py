from dmi_core.engine import DMIEngine
from dmi_core.services import FinancialStatementService


def test_dmi_engine():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    engine = DMIEngine()

    report = engine.analyze(
        statement=statement,
        current_price=10.0,
    )

    assert report.symbol == "AAA"
    assert report.analysis is not None
    assert report.valuation is not None
    assert report.decision is not None

    print("=" * 60)
    print("DMI ENGINE REPORT")
    print("=" * 60)
    print("Symbol         :", report.symbol)
    print("Year           :", report.year)
    print("Quarter        :", report.quarter)
    print("-" * 60)
    print("Financial Score:", report.analysis.overall_score)
    print("Rating         :", report.analysis.overall_rating)
    print("Analysis Rec   :", report.analysis.recommendation)
    print("-" * 60)
    print("Valuation      :", report.valuation.recommendation)
    print("Intrinsic Value:", report.valuation.intrinsic_value)
    print("MOS            :", report.valuation.margin_of_safety)
    print("-" * 60)
    print("Decision       :", report.decision.recommendation)
    print("Confidence     :", report.decision.confidence)
    print("Stars          :", report.decision.stars)
    print("Summary        :", report.decision.summary)
    print("=" * 60)


if __name__ == "__main__":
    test_dmi_engine()