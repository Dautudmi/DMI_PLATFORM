from __future__ import annotations

from collections.abc import Mapping

from dmi_core.market.market_data import MarketData
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)
from dmi_core.valuation.valuation_registry import (
    ValuationModelType,
    ValuationRegistry,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation.weighted_fair_value import (
    WeightedFairValueEngine,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


class ValuationEngineV2:
    """
    Valuation engine sử dụng đồng thời:

        FinancialStatement
                +
            MarketData

    V2 được phát triển song song với ValuationEngine V1.

    Responsibility:
    - kiểm tra FinancialStatement và MarketData
    - lấy model từ ValuationRegistry
    - thực thi từng valuation model
    - cô lập lỗi của từng model
    - tổng hợp Weighted Fair Value

    Không:
    - tải dữ liệu tài chính
    - tải dữ liệu thị trường
    - tạo quyết định đầu tư cuối cùng
    """

    def __init__(
        self,
        registry: ValuationRegistry | None = None,
        config: ValuationConfig | None = None,
    ) -> None:
        if registry is None:
            registry = ValuationRegistry.default()

        if config is None:
            config = ValuationConfig()

        self._registry = registry
        self._config = config

    @property
    def registry(
        self,
    ) -> ValuationRegistry:
        return self._registry

    @property
    def config(
        self,
    ) -> ValuationConfig:
        return self._config

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
        method: str | None = None,
    ) -> ValuationResult:
        """
        Thực thi một valuation model.

        Nếu method=None:
            sử dụng model đầu tiên trong registry.

        Ví dụ:
            method="PE"
            method="PEValuation"
            method="PB"
            method="EVEBITDA"
        """

        self._validate_inputs(
            statement=statement,
            market=market,
        )

        model_type = self._resolve_model(
            method=method,
        )

        return self._evaluate_model(
            model_type=model_type,
            statement=statement,
            market=market,
        )

    def evaluate_all(
        self,
        statement: FinancialStatement,
        market: MarketData,
        continue_on_error: bool = True,
    ) -> tuple[ValuationResult, ...]:
        """
        Thực thi toàn bộ model đã đăng ký.

        continue_on_error=True:
            lỗi của một model được chuyển thành
            ValuationResult có recommendation='N/A'.

        continue_on_error=False:
            exception được raise ngay.
        """

        self._validate_inputs(
            statement=statement,
            market=market,
        )

        results: list[ValuationResult] = []

        for model_type in self._registry.models():
            try:
                result = self._evaluate_model(
                    model_type=model_type,
                    statement=statement,
                    market=market,
                )

            except Exception as exc:
                if not continue_on_error:
                    raise

                result = self._create_error_result(
                    model_type=model_type,
                    market=market,
                    error=exc,
                )

            results.append(result)

        return tuple(results)

    def evaluate_weighted(
        self,
        statement: FinancialStatement,
        market: MarketData,
        weights: Mapping[str, float] | None = None,
        continue_on_error: bool = True,
    ) -> WeightedFairValueResult:
        """
        Thực thi toàn bộ model và tổng hợp
        thành Weighted Fair Value.
        """

        valuation_results = self.evaluate_all(
            statement=statement,
            market=market,
            continue_on_error=continue_on_error,
        )

        weighted_engine = self._create_weighted_engine()

        return weighted_engine.aggregate(
            results=valuation_results,
            weights=weights,
            current_price=market.current_price,
        )

    def evaluate_by_method(
        self,
        statement: FinancialStatement,
        market: MarketData,
        method: str,
    ) -> ValuationResult:
        """
        Alias rõ nghĩa cho evaluate(..., method=...).
        """

        return self.evaluate(
            statement=statement,
            market=market,
            method=method,
        )

    def available_methods(
        self,
    ) -> tuple[str, ...]:
        """
        Trả về tên class của các model đã đăng ký.
        """

        return tuple(
            model_type.__name__
            for model_type in self._registry.models()
        )

    def _evaluate_model(
        self,
        model_type: ValuationModelType,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:
        """
        Khởi tạo và thực thi một model V2.

        Hỗ trợ hai kiểu model trong giai đoạn chuyển tiếp:

        Kiểu mới:
            model_type()
            model.evaluate(
                statement=statement,
                market=market,
            )

        Kiểu có config:
            model_type(config=config)
            model.evaluate(
                statement=statement,
                market=market,
            )
        """

        model = self._create_model(
            model_type=model_type,
        )

        return model.evaluate(
            statement=statement,
            market=market,
        )

    def _create_model(
        self,
        model_type: ValuationModelType,
    ) -> object:
        """
        Khởi tạo valuation model V2.

        Ưu tiên truyền config nếu model hỗ trợ.
        Nếu không, khởi tạo không tham số.
        """

        try:
            return model_type(
                config=self._config,
            )

        except TypeError as config_error:
            try:
                return model_type()

            except TypeError:
                raise config_error

    def _resolve_model(
        self,
        method: str | None,
    ) -> ValuationModelType:
        models = self._registry.models()

        if not models:
            raise RuntimeError(
                "valuation registry has no models"
            )

        if method is None:
            return models[0]

        normalized_method = (
            self._normalize_required_text(
                value=method,
                field_name="method",
            ).lower()
        )

        for model_type in models:
            class_name = model_type.__name__.lower()

            short_name = self._get_short_method_name(
                model_type
            ).lower()

            if normalized_method in {
                class_name,
                short_name,
            }:
                return model_type

        raise ValueError(
            "valuation method is not registered: "
            f"{method}"
        )

    def _create_weighted_engine(
        self,
    ) -> WeightedFairValueEngine:
        return WeightedFairValueEngine(
            required_margin_of_safety=(
                self._config.required_margin_of_safety
            ),
            source=self._config.source,
            schema_version=self._config.schema_version,
        )

    def _create_error_result(
        self,
        model_type: ValuationModelType,
        market: MarketData,
        error: Exception,
    ) -> ValuationResult:
        method = self._get_short_method_name(
            model_type
        )

        return ValuationResult(
            method=method,
            intrinsic_value=None,
            current_price=market.current_price,
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="N/A",
            description=(
                f"{model_type.__name__} failed: "
                f"{error}"
            ),
            source=self._config.source,
            schema_version=self._config.schema_version,
        )

    def _get_short_method_name(
        self,
        model_type: ValuationModelType,
    ) -> str:
        class_name = model_type.__name__
        suffix = "Valuation"

        if class_name.endswith(suffix):
            short_name = class_name[:-len(suffix)]

            if short_name:
                return short_name.upper()

        return class_name.upper()

    def _validate_inputs(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> None:
        self._validate_statement(
            statement=statement,
        )

        self._validate_market(
            market=market,
        )

    def _validate_statement(
        self,
        statement: FinancialStatement,
    ) -> None:
        if statement is None:
            raise ValueError(
                "statement must not be None"
            )

        if not hasattr(
            statement,
            "balance_sheet",
        ):
            raise TypeError(
                "statement must have balance_sheet"
            )

        if not hasattr(
            statement,
            "income_statement",
        ):
            raise TypeError(
                "statement must have income_statement"
            )

    def _validate_market(
        self,
        market: MarketData,
    ) -> None:
        if market is None:
            raise ValueError(
                "market must not be None"
            )

        if not hasattr(
            market,
            "symbol",
        ):
            raise TypeError(
                "market must have symbol"
            )

        if not hasattr(
            market,
            "current_price",
        ):
            raise TypeError(
                "market must have current_price"
            )

    def _normalize_required_text(
        self,
        value: str,
        field_name: str,
    ) -> str:
        if (
            value is None
            or not str(value).strip()
        ):
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return str(value).strip()