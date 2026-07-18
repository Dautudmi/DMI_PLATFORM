from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apps.analysis.analysis_result import (
    AnalysisResult,
)
from dmi_core.analysis.financial_analysis import (
    FinancialAnalysis,
)
from dmi_core.decision.decision_engine import (
    DecisionEngine,
)
from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.providers.financial_statement_provider import (
    FinancialStatementProvider,
)
from dmi_core.valuation.valuation_engine import (
    ValuationEngine,
)


class AnalysisPipeline:
    """
    Production analysis pipeline for one stock symbol.

    Flow:

        FinancialStatementProvider
            ↓
        FinancialStatement
            ↓
        FinancialAnalysis
            ↓
        FinancialAnalysisResult
            ↓
        ValuationEngine
            ↓
        ValuationResult(s)
            ↓
        WeightedFairValueResult
            ↓
        DecisionEngine
            ↓
        DecisionResult
            ↓
        AnalysisResult

    Responsibility:
    - điều phối toàn bộ quy trình phân tích
    - không tự tính financial metrics
    - không tự định giá
    - không tự đưa ra quyết định đầu tư
    - gom kết quả thành một AnalysisResult duy nhất
    """

    def __init__(
        self,
        statement_provider: FinancialStatementProvider,
        valuation_engine: ValuationEngine | None = None,
        decision_engine: DecisionEngine | None = None,
        default_policy: DecisionPolicy | None = None,
    ) -> None:
        """
        Khởi tạo production pipeline.

        Parameters
        ----------
        statement_provider:
            Provider dùng để tải và xây dựng
            FinancialStatement.

        valuation_engine:
            Engine định giá. Nếu None, sử dụng
            ValuationEngine mặc định.

        decision_engine:
            Engine ra quyết định. Nếu None, sử dụng
            DecisionEngine mặc định.

        default_policy:
            Chính sách ra quyết định mặc định.
            Nếu None, sử dụng DecisionPolicy().
        """

        if statement_provider is None:
            raise ValueError(
                "statement_provider must not be None"
            )

        if not isinstance(
            statement_provider,
            FinancialStatementProvider,
        ):
            raise TypeError(
                "statement_provider must be a "
                "FinancialStatementProvider"
            )

        if valuation_engine is None:
            valuation_engine = ValuationEngine()

        if not isinstance(
            valuation_engine,
            ValuationEngine,
        ):
            raise TypeError(
                "valuation_engine must be a "
                "ValuationEngine"
            )

        if decision_engine is None:
            decision_engine = DecisionEngine()

        if not isinstance(
            decision_engine,
            DecisionEngine,
        ):
            raise TypeError(
                "decision_engine must be a "
                "DecisionEngine"
            )

        if default_policy is None:
            default_policy = DecisionPolicy()

        if not isinstance(
            default_policy,
            DecisionPolicy,
        ):
            raise TypeError(
                "default_policy must be a "
                "DecisionPolicy"
            )

        self._statement_provider = (
            statement_provider
        )

        self._valuation_engine = (
            valuation_engine
        )

        self._decision_engine = (
            decision_engine
        )

        self._default_policy = (
            default_policy
        )

    @property
    def statement_provider(
        self,
    ) -> FinancialStatementProvider:
        return self._statement_provider

    @property
    def valuation_engine(
        self,
    ) -> ValuationEngine:
        return self._valuation_engine

    @property
    def decision_engine(
        self,
    ) -> DecisionEngine:
        return self._decision_engine

    @property
    def default_policy(
        self,
    ) -> DecisionPolicy:
        return self._default_policy

    def run(
        self,
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
        Chạy toàn bộ pipeline cho một mã cổ phiếu.

        Parameters
        ----------
        symbol:
            Mã cổ phiếu, ví dụ FPT, HPG, MBB.

        current_price:
            Giá thị trường hiện tại.

        period:
            Kỳ báo cáo:
            - NAM
            - QUY

        page_size:
            Số kỳ dữ liệu yêu cầu từ provider.

        weights:
            Trọng số các phương pháp định giá.

            Ví dụ:

                {
                    "PE": 0.40,
                    "PB": 0.30,
                    "EVEBITDA": 0.20,
                    "DCF": 0.10,
                }

        policy:
            DecisionPolicy riêng cho lần chạy này.
            Nếu None, dùng default_policy.

        continue_on_valuation_error:
            True:
                model định giá lỗi sẽ được cô lập và
                pipeline tiếp tục với model còn lại.

            False:
                lỗi valuation được raise.

        raise_on_error:
            True:
                raise exception khi pipeline lỗi.

            False:
                trả về AnalysisResult không thành công,
                lỗi được lưu trong metadata.
        """

        normalized_symbol = (
            self._normalize_symbol(
                symbol
            )
        )

        self._validate_current_price(
            current_price
        )

        resolved_policy = (
            self._resolve_policy(
                policy
            )
        )

        result = AnalysisResult(
            symbol=normalized_symbol,
            provider_name=(
                self._statement_provider.provider_name
            ),
            schema_version=(
                self._statement_provider.schema_version
            ),
        )

        result.add_metadata(
            "period",
            str(period).strip().upper(),
        )

        result.add_metadata(
            "page_size",
            page_size,
        )

        result.add_metadata(
            "current_price",
            current_price,
        )

        result.add_metadata(
            "pipeline",
            self.__class__.__name__,
        )

        try:
            provider_result = (
                self._statement_provider.get(
                    symbol=normalized_symbol,
                    period=period,
                    page_size=page_size,
                    raise_on_error=raise_on_error,
                )
            )

            result.add_metadata(
                "provider_succeeded",
                provider_result.succeeded,
            )

            result.add_metadata(
                "provider_warnings",
                tuple(
                    provider_result.warnings
                ),
            )

            result.add_metadata(
                "provider_errors",
                tuple(
                    provider_result.errors
                ),
            )

            result.add_metadata(
                "provider_source",
                provider_result.source,
            )

            if not provider_result.succeeded:
                message = (
                    "Financial statement provider "
                    "did not produce a valid statement."
                )

                result.add_metadata(
                    "pipeline_error",
                    message,
                )

                if raise_on_error:
                    raise RuntimeError(
                        provider_result.explain()
                    )

                return result

            statement = (
                provider_result.statement
            )

            if statement is None:
                message = (
                    "ProviderResult succeeded but "
                    "statement is None."
                )

                result.add_metadata(
                    "pipeline_error",
                    message,
                )

                if raise_on_error:
                    raise RuntimeError(
                        message
                    )

                return result

            result.statement = statement

            financial_analysis = (
                FinancialAnalysis(
                    statement=statement
                ).analyze()
            )

            result.financial_analysis = (
                financial_analysis
            )

            valuation_results = (
                self._valuation_engine.evaluate_all(
                    statement=statement,
                    current_price=current_price,
                    continue_on_error=(
                        continue_on_valuation_error
                    ),
                )
            )

            result.valuation_result = (
                valuation_results
            )

            weighted_valuation = (
                self._valuation_engine.evaluate_weighted(
                    statement=statement,
                    current_price=current_price,
                    weights=weights,
                    continue_on_error=(
                        continue_on_valuation_error
                    ),
                )
            )

            result.weighted_valuation = (
                weighted_valuation
            )

            decision = (
                self._decision_engine.evaluate(
                    analysis=financial_analysis,
                    valuation=weighted_valuation,
                    policy=resolved_policy,
                )
            )

            result.decision = decision

            result.add_metadata(
                "valuation_methods",
                tuple(
                    valuation.method
                    for valuation
                    in valuation_results
                ),
            )

            result.add_metadata(
                "valuation_count",
                len(
                    valuation_results
                ),
            )

            result.add_metadata(
                "weighted_method",
                weighted_valuation.method,
            )

            result.add_metadata(
                "weighted_intrinsic_value",
                weighted_valuation.intrinsic_value,
            )

            result.add_metadata(
                "weighted_recommendation",
                weighted_valuation.recommendation,
            )

            result.add_metadata(
                "pipeline_succeeded",
                result.succeeded,
            )

            return result

        except Exception as exc:
            result.add_metadata(
                "pipeline_succeeded",
                False,
            )

            result.add_metadata(
                "pipeline_error_type",
                exc.__class__.__name__,
            )

            result.add_metadata(
                "pipeline_error",
                str(exc),
            )

            if raise_on_error:
                raise

            return result

    def analyze(
        self,
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
        Alias rõ nghĩa cho run().
        """

        return self.run(
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

    def _resolve_policy(
        self,
        policy: DecisionPolicy | None,
    ) -> DecisionPolicy:
        if policy is None:
            return self._default_policy

        if not isinstance(
            policy,
            DecisionPolicy,
        ):
            raise TypeError(
                "policy must be a DecisionPolicy"
            )

        return policy

    def _normalize_symbol(
        self,
        symbol: str,
    ) -> str:
        if symbol is None:
            raise ValueError(
                "symbol must not be empty"
            )

        normalized_symbol = str(
            symbol
        ).strip().upper()

        if not normalized_symbol:
            raise ValueError(
                "symbol must not be empty"
            )

        return normalized_symbol

    def _validate_current_price(
        self,
        current_price: float | None,
    ) -> None:
        if current_price is None:
            return

        if isinstance(
            current_price,
            bool,
        ):
            raise TypeError(
                "current_price must be numeric"
            )

        if not isinstance(
            current_price,
            (int, float),
        ):
            raise TypeError(
                "current_price must be numeric"
            )

        if current_price <= 0:
            raise ValueError(
                "current_price must be greater "
                "than zero"
            )

    def explain_result(
        self,
        result: AnalysisResult,
    ) -> str:
        """
        Tạo phần giải thích ngắn cho kết quả pipeline.
        """

        if result is None:
            raise ValueError(
                "result must not be None"
            )

        if not isinstance(
            result,
            AnalysisResult,
        ):
            raise TypeError(
                "result must be an AnalysisResult"
            )

        lines = [
            "DMI Analysis Pipeline",
            f"Symbol: {result.symbol}",
            (
                "Provider: "
                f"{result.provider_name or 'N/A'}"
            ),
            f"Success: {result.succeeded}",
        ]

        if result.financial_analysis is not None:
            lines.extend(
                [
                    "",
                    "Financial Analysis:",
                    (
                        "Score: "
                        f"{getattr(
                            result.financial_analysis,
                            'overall_score',
                            'N/A',
                        )}"
                    ),
                    (
                        "Rating: "
                        f"{getattr(
                            result.financial_analysis,
                            'overall_rating',
                            'N/A',
                        )}"
                    ),
                    (
                        "Recommendation: "
                        f"{getattr(
                            result.financial_analysis,
                            'recommendation',
                            'N/A',
                        )}"
                    ),
                ]
            )

        if result.weighted_valuation is not None:
            lines.extend(
                [
                    "",
                    "Weighted Valuation:",
                    (
                        "Intrinsic Value: "
                        f"{getattr(
                            result.weighted_valuation,
                            'intrinsic_value',
                            'N/A',
                        )}"
                    ),
                    (
                        "Recommendation: "
                        f"{getattr(
                            result.weighted_valuation,
                            'recommendation',
                            'N/A',
                        )}"
                    ),
                ]
            )

        if result.decision is not None:
            lines.extend(
                [
                    "",
                    "Decision:",
                    str(
                        result.decision
                    ),
                ]
            )

        pipeline_error = (
            result.get_metadata(
                "pipeline_error"
            )
        )

        if pipeline_error:
            lines.extend(
                [
                    "",
                    "Error:",
                    str(
                        pipeline_error
                    ),
                ]
            )

        return "\n".join(
            lines
        )