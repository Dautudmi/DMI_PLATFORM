from dmi_core.models.analysis_result import AnalysisResult
from dmi_core.rules.base_rule import BaseRule


class LeverageRules(BaseRule):
    """
    Leverage rules for DMI Platform.
    """

    @staticmethod
    def evaluate(debt_to_equity: float | None) -> AnalysisResult:
        """
        Evaluate leverage based on Debt to Equity.
        """

        if debt_to_equity is None:
            return AnalysisResult(
                code="LEVERAGE",
                name="Leverage",
                rating="Unknown",
                score=0,
                summary="Không đủ dữ liệu để đánh giá đòn bẩy tài chính.",
                recommendation="Kiểm tra lại dữ liệu tổng nợ và vốn chủ sở hữu.",
            )

        if debt_to_equity <= 0.5:
            rating = "Excellent"
            score = 100
            summary = "Đòn bẩy tài chính rất thấp."
            recommendation = "Cấu trúc vốn an toàn."
        elif debt_to_equity <= 1.0:
            rating = "Good"
            score = 80
            summary = "Đòn bẩy tài chính ở mức hợp lý."
            recommendation = "Rủi ro tài chính được kiểm soát."
        elif debt_to_equity <= 1.5:
            rating = "Average"
            score = 60
            summary = "Đòn bẩy tài chính ở mức trung bình."
            recommendation = "Cần theo dõi khả năng trả nợ và dòng tiền."
        elif debt_to_equity <= 2.0:
            rating = "Weak"
            score = 40
            summary = "Đòn bẩy tài chính khá cao."
            recommendation = "Cần thận trọng với rủi ro tài chính."
        else:
            rating = "Poor"
            score = 20
            summary = "Đòn bẩy tài chính rất cao."
            recommendation = "Rủi ro tài chính lớn nếu dòng tiền suy yếu."

        return AnalysisResult(
            code="LEVERAGE",
            name="Leverage",
            rating=rating,
            score=score,
            summary=summary,
            recommendation=recommendation,
        )