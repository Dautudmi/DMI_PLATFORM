from __future__ import annotations

from collections.abc import Mapping

from apps.analysis.analysis_pipeline import (
    AnalysisPipeline,
)
from apps.analysis.analysis_result import (
    AnalysisResult,
)
from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)


def analyze_symbol(
    pipeline: AnalysisPipeline,
    symbol: str,
    current_price: float | None = None,
    period: str = "NAM",
    page_size: int = 4,
    weights: Mapping[
        str,
        float,
    ] | None = None,
    policy: DecisionPolicy | None = None,
    continue_on_valuation_error: bool = True,
    raise_on_error: bool = False,
) -> AnalysisResult:
    """
    Analyze one stock symbol through AnalysisPipeline.

    Đây là application-level use case giúp các lớp bên ngoài
    không cần gọi trực tiếp nhiều engine.

    Flow:

        analyze_symbol(...)
            ↓
        AnalysisPipeline.run(...)
            ↓
        AnalysisResult

    Parameters
    ----------
    pipeline:
        AnalysisPipeline đã được cấu hình provider và engine.

    symbol:
        Mã cổ phiếu cần phân tích.

    current_price:
        Giá thị trường hiện tại.

    period:
        Kỳ báo cáo:
        - NAM
        - QUY

    page_size:
        Số kỳ báo cáo được tải từ provider.

    weights:
        Trọng số các phương pháp định giá.

    policy:
        DecisionPolicy riêng cho lần phân tích.

    continue_on_valuation_error:
        Có tiếp tục khi một valuation model bị lỗi hay không.

    raise_on_error:
        True:
            lỗi được raise.

        False:
            lỗi được lưu trong AnalysisResult.metadata.
    """

    if pipeline is None:
        raise ValueError(
            "pipeline must not be None"
        )

    if not isinstance(
        pipeline,
        AnalysisPipeline,
    ):
        raise TypeError(
            "pipeline must be an AnalysisPipeline"
        )

    return pipeline.run(
        symbol=symbol,
        current_price=current_price,
        period=period,
        page_size=page_size,
        weights=weights,
        policy=policy,
        continue_on_valuation_error=(
            continue_on_valuation_error
        ),
        raise_on_error=raise_on_error,
    )


def analyze_and_explain(
    pipeline: AnalysisPipeline,
    symbol: str,
    current_price: float | None = None,
    period: str = "NAM",
    page_size: int = 4,
    weights: Mapping[
        str,
        float,
    ] | None = None,
    policy: DecisionPolicy | None = None,
    continue_on_valuation_error: bool = True,
    raise_on_error: bool = False,
) -> tuple[
    AnalysisResult,
    str,
]:
    """
    Analyze one symbol and return both:

    - AnalysisResult
    - human-readable explanation
    """

    result = analyze_symbol(
        pipeline=pipeline,
        symbol=symbol,
        current_price=current_price,
        period=period,
        page_size=page_size,
        weights=weights,
        policy=policy,
        continue_on_valuation_error=(
            continue_on_valuation_error
        ),
        raise_on_error=raise_on_error,
    )

    explanation = pipeline.explain_result(
        result
    )

    return (
        result,
        explanation,
    )