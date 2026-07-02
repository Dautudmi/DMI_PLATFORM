from dmi_core.models.analysis_result import AnalysisResult
from dmi_core.rules.base_rule import BaseRule


class ProfitabilityRules(BaseRule):
    """
    Profitability rules for DMI Platform.
    """

    @staticmethod
    def evaluate(roe: float | None) -> AnalysisResult:
        """
        Evaluate profitability based on ROE.
        """

        if roe is None:
            return AnalysisResult(
                code="PROFITABILITY",
                name="Profitability",
                rating="Unknown",
                score=0,
                summary="Không đủ dữ liệu để đánh giá khả năng sinh lời.",
                recommendation="Kiểm tra lại dữ liệu lợi nhuận và vốn chủ sở hữu.",
            )

        if roe >= 0.20:
            rating = "Excellent"
            score = 100
            summary = "Khả năng sinh lời rất mạnh."
            recommendation = "Doanh nghiệp có hiệu quả sử dụng vốn chủ sở hữu rất tốt."
        elif roe >= 0.15:
            rating = "Good"
            score = 80
            summary = "Khả năng sinh lời tốt."
            recommendation = "Có thể tiếp tục theo dõi cho mục tiêu đầu tư chất lượng."
        elif roe >= 0.10:
            rating = "Average"
            score = 60
            summary = "Khả năng sinh lời ở mức trung bình."
            recommendation = "Nên kết hợp thêm biên lợi nhuận, tăng trưởng và đòn bẩy."
        elif roe >= 0.05:
            rating = "Weak"
            score = 40
            summary = "Khả năng sinh lời thấp."
            recommendation = "Cần phân tích nguyên nhân ROE thấp trước khi đầu tư."
        else:
            rating = "Poor"
            score = 20
            summary = "Hiệu quả sử dụng vốn rất thấp."
            recommendation = "Không phù hợp cho đầu tư dài hạn nếu không có yếu tố cải thiện rõ ràng."

        return AnalysisResult(
            code="PROFITABILITY",
            name="Profitability",
            rating=rating,
            score=score,
            summary=summary,
            recommendation=recommendation,
        )