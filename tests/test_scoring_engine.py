from dmi_core.models.analysis_result import AnalysisResult
from dmi_core.scoring import ScoringEngine


def test_scoring_engine():

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

    score, rating, recommendation = ScoringEngine.evaluate(
        [
            profitability,
            leverage,
        ]
    )

    assert score == 40
    assert rating == "D"
    assert recommendation == "CAUTION"

    print("=" * 60)
    print("SCORING ENGINE")
    print("=" * 60)
    print("Score          :", score)
    print("Rating         :", rating)
    print("Recommendation :", recommendation)
    print("=" * 60)


if __name__ == "__main__":
    test_scoring_engine()