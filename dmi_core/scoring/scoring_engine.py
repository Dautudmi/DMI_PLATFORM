from dmi_core.models.analysis_result import AnalysisResult


class ScoringEngine:
    """
    DMI Scoring Engine.

    Converts multiple AnalysisResult objects into:
    - overall_score
    - overall_rating
    - recommendation
    """

    @staticmethod
    def calculate_score(results: list[AnalysisResult]) -> float:
        """
        Calculate average score from analysis results.
        """

        valid_scores = [
            result.score
            for result in results
            if result is not None
        ]

        if not valid_scores:
            return 0.0

        return sum(valid_scores) / len(valid_scores)

    @staticmethod
    def rating_from_score(score: float) -> str:
        """
        Convert numeric score to rating.
        """

        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 55:
            return "C"
        if score >= 40:
            return "D"
        return "E"

    @staticmethod
    def recommendation_from_score(score: float) -> str:
        """
        Convert numeric score to investment recommendation.
        """

        if score >= 85:
            return "BUY"
        if score >= 70:
            return "ACCUMULATE"
        if score >= 55:
            return "WATCH"
        if score >= 40:
            return "CAUTION"
        return "AVOID"

    @staticmethod
    def evaluate(results: list[AnalysisResult]) -> tuple[float, str, str]:
        """
        Evaluate overall company score.
        """

        score = ScoringEngine.calculate_score(results)
        rating = ScoringEngine.rating_from_score(score)
        recommendation = ScoringEngine.recommendation_from_score(score)

        return score, rating, recommendation