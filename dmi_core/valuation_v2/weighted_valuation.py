from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation_v2.valuation_engine import (
    ValuationEngineV2Result,
)


@dataclass(slots=True)
class WeightedValuationResult:
    """
    Kết quả tổng hợp nhiều valuation method.

    weighted_fair_value:
        Giá trị hợp lý tổng hợp theo trọng số.

    current_price:
        Giá thị trường hiện tại.

    upside:
        Mức tăng từ giá hiện tại đến fair value.

    margin_of_safety:
        Biên an toàn theo fair value tổng hợp.

    recommendation:
        BUY / HOLD / SELL / N/A.

    applied_weights:
        Trọng số thực tế sau khi loại bỏ các model
        không có intrinsic value hợp lệ.
    """

    symbol: str

    weighted_fair_value: float | None

    current_price: float | None

    upside: float | None

    downside: float | None

    margin_of_safety: float | None

    recommendation: str

    applied_weights: dict[
        str,
        float,
    ]

    included_methods: tuple[
        str,
        ...,
    ]

    excluded_methods: tuple[
        str,
        ...,
    ]

    description: str | None = None

    source: str = "DMI"

    schema_version: str = "2.0"

    @property
    def succeeded(
        self,
    ) -> bool:
        return (
            self.weighted_fair_value is not None
            and self.weighted_fair_value > 0
        )


class WeightedValuationV2:
    """
    Tổng hợp kết quả từ nhiều valuation model.

    Trọng số mặc định:

        PE          40%
        PB          30%
        EV/EBITDA   30%

    Nếu một method không có intrinsic value hợp lệ,
    method đó bị loại và các trọng số còn lại sẽ được
    chuẩn hóa lại về tổng 100%.
    """

    DEFAULT_WEIGHTS: dict[
        str,
        float,
    ] = {
        "PE": 0.40,
        "PB": 0.30,
        "EV/EBITDA": 0.30,
    }

    def __init__(
        self,
        weights: Mapping[
            str,
            float,
        ] | None = None,
        required_margin_of_safety: float = 0.25,
        source: str = "DMI",
        schema_version: str = "2.0",
    ) -> None:
        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        self._weights = self._normalize_input_weights(
            weights
        )

        self._required_margin_of_safety = (
            self._validate_required_margin_of_safety(
                required_margin_of_safety
            )
        )

        self._source = str(
            source
        )

        self._schema_version = str(
            schema_version
        )

    @property
    def weights(
        self,
    ) -> dict[
        str,
        float,
    ]:
        return dict(
            self._weights
        )

    @property
    def required_margin_of_safety(
        self,
    ) -> float:
        return self._required_margin_of_safety

    def evaluate(
        self,
        engine_result: ValuationEngineV2Result,
    ) -> WeightedValuationResult:
        """
        Tổng hợp fair value từ kết quả ValuationEngineV2.
        """

        if engine_result is None:
            raise ValueError(
                "engine_result must not be None"
            )

        symbol = self._normalize_symbol(
            engine_result.symbol
        )

        available_results = (
            self._collect_available_results(
                engine_result=engine_result,
            )
        )

        excluded_methods = tuple(
            result.method
            for result in engine_result.results
            if result.method not in available_results
        )

        if not available_results:
            return WeightedValuationResult(
                symbol=symbol,
                weighted_fair_value=None,
                current_price=(
                    self._resolve_current_price(
                        engine_result.results
                    )
                ),
                upside=None,
                downside=None,
                margin_of_safety=None,
                recommendation="N/A",
                applied_weights={},
                included_methods=(),
                excluded_methods=excluded_methods,
                description=(
                    "Unable to calculate weighted fair "
                    "value because no valuation method "
                    "returned a valid intrinsic value."
                ),
                source=self._source,
                schema_version=self._schema_version,
            )

        applied_weights = self._build_applied_weights(
            available_results=available_results,
        )

        weighted_fair_value = sum(
            available_results[method].intrinsic_value
            * weight
            for method, weight in (
                applied_weights.items()
            )
            if (
                available_results[method].intrinsic_value
                is not None
            )
        )

        current_price = self._resolve_current_price(
            tuple(
                available_results.values()
            )
        )

        upside = self._calculate_upside(
            weighted_fair_value=weighted_fair_value,
            current_price=current_price,
        )

        downside = self._calculate_downside(
            upside=upside,
        )

        margin_of_safety = (
            self._calculate_margin_of_safety(
                weighted_fair_value=(
                    weighted_fair_value
                ),
                current_price=current_price,
            )
        )

        recommendation = self._create_recommendation(
            margin_of_safety=margin_of_safety,
        )

        included_methods = tuple(
            applied_weights.keys()
        )

        description = (
            "Weighted valuation completed using "
            f"{', '.join(included_methods)}."
        )

        return WeightedValuationResult(
            symbol=symbol,
            weighted_fair_value=weighted_fair_value,
            current_price=current_price,
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            applied_weights=applied_weights,
            included_methods=included_methods,
            excluded_methods=excluded_methods,
            description=description,
            source=self._source,
            schema_version=self._schema_version,
        )

    def _collect_available_results(
        self,
        engine_result: ValuationEngineV2Result,
    ) -> dict[
        str,
        ValuationResult,
    ]:
        """
        Chỉ giữ lại các method:

        - có trong weight config
        - có intrinsic value dương
        """

        available_results: dict[
            str,
            ValuationResult,
        ] = {}

        for result in engine_result.results:
            method = self._normalize_method(
                result.method
            )

            if method not in self._weights:
                continue

            intrinsic_value = (
                self._positive_or_none(
                    result.intrinsic_value
                )
            )

            if intrinsic_value is None:
                continue

            available_results[
                method
            ] = result

        return available_results

    def _build_applied_weights(
        self,
        available_results: Mapping[
            str,
            ValuationResult,
        ],
    ) -> dict[
        str,
        float,
    ]:
        """
        Chuẩn hóa lại trọng số cho các method khả dụng.
        """

        selected_weights = {
            method: self._weights[method]
            for method in available_results
        }

        total_weight = sum(
            selected_weights.values()
        )

        if total_weight <= 0:
            raise ValueError(
                "total selected weight must be "
                "greater than zero"
            )

        return {
            method: weight / total_weight
            for method, weight in (
                selected_weights.items()
            )
        }

    def _create_recommendation(
        self,
        margin_of_safety: float | None,
    ) -> str:
        if margin_of_safety is None:
            return "N/A"

        if (
            margin_of_safety
            >= self._required_margin_of_safety
        ):
            return "BUY"

        if margin_of_safety > 0:
            return "HOLD"

        return "SELL"

    @staticmethod
    def _resolve_current_price(
        results: tuple[
            ValuationResult,
            ...,
        ],
    ) -> float | None:
        """
        Lấy current price hợp lệ đầu tiên.
        """

        for result in results:
            current_price = (
                WeightedValuationV2._positive_or_none(
                    result.current_price
                )
            )

            if current_price is not None:
                return current_price

        return None

    @staticmethod
    def _calculate_upside(
        weighted_fair_value: float | None,
        current_price: float | None,
    ) -> float | None:
        if (
            weighted_fair_value is None
            or weighted_fair_value <= 0
            or current_price is None
            or current_price <= 0
        ):
            return None

        return (
            weighted_fair_value
            / current_price
            - 1.0
        )

    @staticmethod
    def _calculate_downside(
        upside: float | None,
    ) -> float | None:
        if upside is None:
            return None

        if upside >= 0:
            return 0.0

        return abs(
            upside
        )

    @staticmethod
    def _calculate_margin_of_safety(
        weighted_fair_value: float | None,
        current_price: float | None,
    ) -> float | None:
        if (
            weighted_fair_value is None
            or weighted_fair_value <= 0
            or current_price is None
            or current_price <= 0
        ):
            return None

        return (
            weighted_fair_value
            - current_price
        ) / weighted_fair_value

    @staticmethod
    def _normalize_input_weights(
        weights: Mapping[
            str,
            float,
        ],
    ) -> dict[
        str,
        float,
    ]:
        if not weights:
            raise ValueError(
                "weights must not be empty"
            )

        normalized_weights: dict[
            str,
            float,
        ] = {}

        for raw_method, raw_weight in (
            weights.items()
        ):
            method = (
                WeightedValuationV2
                ._normalize_method(
                    raw_method
                )
            )

            try:
                weight = float(
                    raw_weight
                )
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    f"weight for {method} must be "
                    "numeric"
                ) from exc

            if weight < 0:
                raise ValueError(
                    f"weight for {method} must not "
                    "be negative"
                )

            if method in normalized_weights:
                raise ValueError(
                    "duplicate valuation method in "
                    f"weights: {method}"
                )

            normalized_weights[
                method
            ] = weight

        if sum(
            normalized_weights.values()
        ) <= 0:
            raise ValueError(
                "total weight must be greater than zero"
            )

        return normalized_weights

    @staticmethod
    def _validate_required_margin_of_safety(
        value: object,
    ) -> float:
        try:
            normalized_value = float(
                value
            )
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "required_margin_of_safety must be "
                "numeric"
            ) from exc

        if not 0 <= normalized_value < 1:
            raise ValueError(
                "required_margin_of_safety must be "
                "between 0 and 1"
            )

        return normalized_value

    @staticmethod
    def _normalize_method(
        method: object,
    ) -> str:
        if method is None:
            raise ValueError(
                "valuation method must not be empty"
            )

        normalized_method = str(
            method
        ).strip().upper()

        if not normalized_method:
            raise ValueError(
                "valuation method must not be empty"
            )

        aliases = {
            "P/E": "PE",
            "PRICE/EARNINGS": "PE",
            "PRICE / EARNINGS": "PE",
            "P/B": "PB",
            "PRICE/BOOK": "PB",
            "PRICE / BOOK": "PB",
            "EV EBITDA": "EV/EBITDA",
            "EV-EBITDA": "EV/EBITDA",
        }

        return aliases.get(
            normalized_method,
            normalized_method,
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

    @staticmethod
    def _positive_or_none(
        value: object,
    ) -> float | None:
        if value is None:
            return None

        try:
            normalized_value = float(
                value
            )
        except (TypeError, ValueError):
            return None

        if normalized_value <= 0:
            return None

        return normalized_value