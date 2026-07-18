from __future__ import annotations

from collections.abc import Mapping

from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.valuation.valuation_config import ValuationConfig
from dmi_core.valuation.valuation_registry import (
    ValuationModelType,
    ValuationRegistry,
)
from dmi_core.valuation.valuation_result import ValuationResult
from dmi_core.valuation.weighted_fair_value import (
    WeightedFairValueEngine,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


class ValuationEngine:
    """
    Valuation engine V1.

    Responsibility:
    - nhận FinancialStatement
    - lấy valuation model từ registry
    - chạy từng model với current_price
    - cô lập lỗi từng model
    - tổng hợp Weighted Fair Value
    """

    def __init__(
        self,
        registry: ValuationRegistry | None = None,
        config: ValuationConfig | None = None,
    ) -> None:
        self._registry = (
            registry
            if registry is not None
            else ValuationRegistry.default()
        )

        self._config = (
            config
            if config is not None
            else ValuationConfig()
        )

    @property
    def registry(self) -> ValuationRegistry:
        return self._registry

    @property
    def config(self) -> ValuationConfig:
        return self._config

    def evaluate(
        self,
        statement: FinancialStatement,
        current_price: float | None = None,
        method: str | None = None,
    ) -> ValuationResult:
        """
        Run one valuation model.

        If method is None, use the first model
        registered in the registry.
        """

        self._validate_statement(statement)

        model_type = self._resolve_model(method)

        return self._evaluate_model(
            model_type=model_type,
            statement=statement,
            current_price=current_price,
        )

    def evaluate_by_method(
        self,
        statement: FinancialStatement,
        method: str,
        current_price: float | None = None,
    ) -> ValuationResult:
        """
        Explicit alias for evaluate(..., method=...).
        """

        return self.evaluate(
            statement=statement,
            current_price=current_price,
            method=method,
        )

    def evaluate_all(
        self,
        statement: FinancialStatement,
        current_price: float | None = None,
        continue_on_error: bool = True,
    ) -> tuple[ValuationResult, ...]:
        """
        Run every registered valuation model.
        """

        self._validate_statement(statement)

        results: list[ValuationResult] = []

        for model_type in self._registry.models():
            try:
                result = self._evaluate_model(
                    model_type=model_type,
                    statement=statement,
                    current_price=current_price,
                )

            except Exception as exc:
                if not continue_on_error:
                    raise

                result = self._create_error_result(
                    model_type=model_type,
                    current_price=current_price,
                    error=exc,
                )

            results.append(result)

        return tuple(results)

    def evaluate_weighted(
        self,
        statement: FinancialStatement,
        current_price: float | None = None,
        weights: Mapping[str, float] | None = None,
        continue_on_error: bool = True,
    ) -> WeightedFairValueResult:
        """
        Run all valuation models and aggregate
        their valid intrinsic values.
        """

        results = self.evaluate_all(
            statement=statement,
            current_price=current_price,
            continue_on_error=continue_on_error,
        )

        weighted_engine = WeightedFairValueEngine(
            required_margin_of_safety=(
                self._config.required_margin_of_safety
            ),
            source=self._config.source,
            schema_version=self._config.schema_version,
        )

        return weighted_engine.aggregate(
            results=results,
            weights=weights,
            current_price=current_price,
        )

    def available_methods(self) -> tuple[str, ...]:
        """
        Return registered valuation class names.
        """

        return tuple(
            model_type.__name__
            for model_type in self._registry.models()
        )

    def _evaluate_model(
        self,
        model_type: ValuationModelType,
        statement: FinancialStatement,
        current_price: float | None,
    ) -> ValuationResult:
        model = self._create_model(
            model_type=model_type,
            statement=statement,
        )

        return model.evaluate(
            current_price=current_price,
        )

    def _create_model(
        self,
        model_type: ValuationModelType,
        statement: FinancialStatement,
    ) -> object:
        """
        Create a valuation model.

        Prefer constructor(statement, config).
        Fall back to constructor(statement) for custom models
        that do not accept config.
        """

        try:
            return model_type(
                statement=statement,
                config=self._config,
            )

        except TypeError as config_error:
            try:
                return model_type(
                    statement=statement,
                )

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

        normalized_method = self._normalize_required_text(
            value=method,
            field_name="method",
        ).lower()

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

    def _create_error_result(
        self,
        model_type: ValuationModelType,
        current_price: float | None,
        error: Exception,
    ) -> ValuationResult:
        method = self._get_short_method_name(
            model_type
        )

        return ValuationResult(
            method=method,
            intrinsic_value=None,
            current_price=current_price,
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="N/A",
            description=(
                f"{model_type.__name__} failed: {error}"
            ),
            source=self._config.source,
            schema_version=self._config.schema_version,
        )

    @staticmethod
    def _get_short_method_name(
        model_type: ValuationModelType,
    ) -> str:
        class_name = model_type.__name__
        suffix = "Valuation"

        if class_name.endswith(suffix):
            short_name = class_name[:-len(suffix)]

            if short_name:
                return short_name.upper()

        return class_name.upper()

    @staticmethod
    def _validate_statement(
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

    @staticmethod
    def _normalize_required_text(
        value: str,
        field_name: str,
    ) -> str:
        if value is None or not str(value).strip():
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return str(value).strip()