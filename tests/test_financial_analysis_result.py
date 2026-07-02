from dmi_core.models.analysis_result import AnalysisResult
from dmi_core.models.financial_analysis_result import FinancialAnalysisResult


def test_financial_analysis_result():

    profitability = AnalysisResult(
        code="PROFITABILITY",
        name="Profitability",
        rating="Poor",
        score=20,
        summary="ROE thấp.",
        recommendation="Không nên đầu tư.",
    )

    leverage = AnalysisResult(
        code="LEVERAGE",
        name="Leverage",
        rating="Average",
        score=60,
        summary="Đòn bẩy trung bình.",
        recommendation="Theo dõi thêm.",
    )

    result = FinancialAnalysisResult(
        profitability=profitability,
        leverage=leverage,
        overall_score=40,
        overall_rating="C",
        recommendation="WATCH",
    )

    assert result.overall_score == 40
    assert result.overall_rating == "C"

    print(result)


if __name__ == "__main__":
    test_financial_analysis_result()