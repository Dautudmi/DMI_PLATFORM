from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from dmi_core.market.market_data import (
    MarketData,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation_v2.base_valuation import (
    BaseValuationV2,
)
from dmi_core.valuation_v2.valuation_registry import (
    ValuationRegistryV2,
)


@dataclass(slots=True)
class ValuationExecutionError:
    """
    Mô tả lỗi của một valuation model riêng lẻ.
    """

    model_name: str
    message: str
    exception_type: str


@dataclass(slots=True)
class ValuationEngineV2Result:
    """
    Kết quả tổng hợp của ValuationEngineV2.

    results:
        Các ValuationResult chạy thành công hoặc trả về N/A.

    errors:
        Các exception phát sinh trong từng model.

    Engine không tự tính weighted fair value ở lớp này.
    Việc tổng hợp fair value sẽ được tách sang bước riêng.
    """

    symbol: str

    results: tuple[
        ValuationResult,
        ...,
    ]

    errors: tuple[
        ValuationExecutionError,
        ...,
    ]

    provider: str | None = None

    schema_version: str = "2.0"

    @property
    def succeeded(
        self,
    ) -> bool:
        """
        Engine được xem là chạy thành công nếu có ít nhất
        một ValuationResult.
        """

        return len(
            self.results
        ) > 0

    @property
    def has_errors(
        self,
    ) -> bool:
        return len(
            self.errors
        ) > 0

    @property
    def available_results(
        self,
    ) -> tuple[
        ValuationResult,
        ...,
    ]:
        """
        Chỉ lấy các kết quả có intrinsic value hợp lệ.
        """

        return tuple(
            result
            for result in self.results
            if (
                result.intrinsic_value is not None
                and result.intrinsic_value > 0
            )
        )

    @property
    def unavailable_results(
        self,
    ) -> tuple[
        ValuationResult,
        ...,
    ]:
        """
        Các model trả về N/A vì thiếu dữ liệu.
        """

        return tuple(
            result
            for result in self.results
            if result.intrinsic_value is None
        )

    @property
    def methods(
        self,
    ) -> tuple[
        str,
        ...,
    ]:
        return tuple(
            result.method
            for result in self.results
        )


class ValuationEngineV2:
    """
    Valuation Engine V2.

    Input:

        FinancialStatement
                +
            MarketData

    Flow:

        Registry V2
            ↓
        Instantiate model
            ↓
        model.evaluate(statement, market)
            ↓
        Collect ValuationResult
            ↓
        Continue or raise on model error

    Engine này hoàn toàn độc lập với ValuationEngine V1.
    """

    def __init__(
        self,
        registry: ValuationRegistryV2 | None = None,
        config: ValuationConfig | None = None,
        continue_on_error: bool = True,
    ) -> None:
        if registry is None:
            registry = ValuationRegistryV2.default()

        if config is None:
            config = ValuationConfig()

        self._registry = registry
        self._config = config
        self._continue_on_error = bool(
            continue_on_error
        )

    @property
    def registry(
        self,
    ) -> ValuationRegistryV2:
        return self._registry

    @property
    def config(
        self,
    ) -> ValuationConfig:
        return self._config

    @property
    def continue_on_error(
        self,
    ) -> bool:
        return self._continue_on_error

    def available_models(
        self,
    ) -> tuple[
        str,
        ...,
    ]:
        """
        Trả về danh sách model class hiện có.
        """

        return self._registry.model_names()

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationEngineV2Result:
        """
        Chạy toàn bộ valuation model trong registry.
        """

        self._validate_inputs(
            statement=statement,
            market=market,
        )

        results: list[
            ValuationResult
        ] = []

        errors: list[
            ValuationExecutionError
        ] = []

        for model_type in self._registry:
            try:
                model = self._create_model(
                    model_type=model_type,
                )

                result = model.evaluate(
                    statement=statement,
                    market=market,
                )

                self._validate_result(
                    model=model,
                    result=result,
                )

                results.append(
                    result
                )

            except Exception as exc:
                error = ValuationExecutionError(
                    model_name=(
                        model_type.__name__
                    ),
                    message=str(
                        exc
                    ),
                    exception_type=(
                        type(exc).__name__
                    ),
                )

                errors.append(
                    error
                )

                if not self._continue_on_error:
                    raise

        return ValuationEngineV2Result(
            symbol=self._normalize_symbol(
                statement.symbol
            ),
            results=tuple(
                results
            ),
            errors=tuple(
                errors
            ),
            provider=market.provider,
        )

    def evaluate_models(
        self,
        statement: FinancialStatement,
        market: MarketData,
        model_types: Iterable[
            type[BaseValuationV2]
        ],
    ) -> ValuationEngineV2Result:
        """
        Chạy một tập model được chỉ định mà không sửa registry.
        """

        self._validate_inputs(
            statement=statement,
            market=market,
        )

        temporary_registry = (
            ValuationRegistryV2(
                models=model_types
            )
        )

        temporary_engine = ValuationEngineV2(
            registry=temporary_registry,
            config=self._config,
            continue_on_error=(
                self._continue_on_error
            ),
        )

        return temporary_engine.evaluate(
            statement=statement,
            market=market,
        )

    def evaluate_model(
        self,
        statement: FinancialStatement,
        market: MarketData,
        model_type: type[
            BaseValuationV2
        ],
    ) -> ValuationResult:
        """
        Chạy duy nhất một valuation model.

        Với method này, exception được raise trực tiếp để
        caller biết chính xác model nào bị lỗi.
        """

        self._validate_inputs(
            statement=statement,
            market=market,
        )

        self._validate_model_type(
            model_type
        )

        model = self._create_model(
            model_type=model_type,
        )

        result = model.evaluate(
            statement=statement,
            market=market,
        )

        self._validate_result(
            model=model,
            result=result,
        )

        return result

    def _create_model(
        self,
        model_type: type[
            BaseValuationV2
        ],
    ) -> BaseValuationV2:
        """
        Khởi tạo model với config chung của engine.
        """

        self._validate_model_type(
            model_type
        )

        return model_type(
            config=self._config
        )

    @staticmethod
    def _validate_model_type(
        model_type: type[
            BaseValuationV2
        ],
    ) -> None:
        if model_type is None:
            raise ValueError(
                "model_type must not be None"
            )

        if not isinstance(
            model_type,
            type,
        ):
            raise TypeError(
                "model_type must be a class"
            )

        if not issubclass(
            model_type,
            BaseValuationV2,
        ):
            raise TypeError(
                "model_type must inherit "
                "BaseValuationV2"
            )

    @staticmethod
    def _validate_result(
        model: BaseValuationV2,
        result: ValuationResult,
    ) -> None:
        if result is None:
            raise ValueError(
                f"{type(model).__name__} returned None"
            )

        if not isinstance(
            result,
            ValuationResult,
        ):
            raise TypeError(
                f"{type(model).__name__} must return "
                "ValuationResult"
            )

    @classmethod
    def _validate_inputs(
        cls,
        statement: FinancialStatement,
        market: MarketData,
    ) -> None:
        if statement is None:
            raise ValueError(
                "statement must not be None"
            )

        if market is None:
            raise ValueError(
                "market must not be None"
            )

        if not isinstance(
            statement,
            FinancialStatement,
        ):
            raise TypeError(
                "statement must be FinancialStatement"
            )

        if not isinstance(
            market,
            MarketData,
        ):
            raise TypeError(
                "market must be MarketData"
            )

        statement_symbol = cls._normalize_symbol(
            statement.symbol
        )

        market_symbol = cls._normalize_symbol(
            market.symbol
        )

        if statement_symbol != market_symbol:
            raise ValueError(
                "statement symbol and market symbol "
                "must be identical"
            )

    @staticmethod
    def _normalize_symbol(
        symbol: object,
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