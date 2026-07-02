from dmi_core.models.analysis_result import AnalysisResult


def test_analysis_result():

    result = AnalysisResult(
        code="PROFITABILITY",
        name="Profitability",
        rating="Weak",
        score=32,
        summary="ROE thấp hơn mức kỳ vọng.",
        recommendation="Cần cải thiện hiệu quả sử dụng vốn.",
    )

    assert result.code == "PROFITABILITY"
    assert result.rating == "Weak"
    assert result.score == 32

    print(result)


if __name__ == "__main__":
    test_analysis_result()