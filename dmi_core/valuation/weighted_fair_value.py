from __future__ import annotations

from collections.abc import (
    Iterable,
    Mapping,
)

from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


class WeightedFairValueEngine:
    """
    Tổng hợp nhiều kết quả định giá thành một fair value.

    Công thức:

        Weighted Fair Value
            = Sum(Intrinsic Value × Weight)
              / Sum(Weight)

    Engine chỉ sử dụng valuation result hợp lệ:

    - intrinsic_value không phải None
    - intrinsic_value lớn hơn 0
    - method không rỗng

    Engine không:
    - tự chạy PEValuation hoặc PBValuation
    - tạo FinancialStatement
    - sửa ValuationRegistry
    - đưa ra quyết định đầu tư cuối cùng
    """

    def __init__(
        self,
        required_margin_of_safety: float = 0.25,
        source: str = "DMI",
        schema_version: str = "3.0",
    ) -> None:
        if required_margin_of_safety < 0:
            raise ValueError(
                "required_margin_of_safety "
                "must not be negative"
            )

        self._required_margin_of_safety = (
            required_margin_of_safety
        )

        self._source = self._normalize_required_text(
            value=source,
            field_name="source",
        )

        self._schema_version = (
            self._normalize_required_text(
                value=schema_version,
                field_name="schema_version",
            )
        )

    @property
    def required_margin_of_safety(
        self,
    ) -> float:
        return self._required_margin_of_safety

    @property
    def source(
        self,
    ) -> str:
        return self._source

    @property
    def schema_version(
        self,
    ) -> str:
        return self._schema_version

    def aggregate(
        self,
        results: Iterable[
            ValuationResult
        ],
        weights: Mapping[
            str,
            float,
        ] | None = None,
        current_price: float | None = None,
    ) -> WeightedFairValueResult:
        """
        Tổng hợp các valuation result.

        Khi weights=None:
            các phương pháp hợp lệ có trọng số bằng nhau.

        Khi weights được truyền:
            chỉ các phương pháp có trọng số lớn hơn 0
            mới được sử dụng.

        current_price:
            - ưu tiên giá được truyền trực tiếp
            - nếu None, dùng current_price đầu tiên có
              trong các valuation result
        """

        all_results = self._prepare_results(
            results
        )

        valid_results = self._get_valid_results(
            all_results
        )

        resolved_price = self._resolve_current_price(
            results=all_results,
            current_price=current_price,
        )

        if not valid_results:
            return self._create_na_result(
                components=all_results,
                current_price=resolved_price,
                description=(
                    "Weighted fair value cannot be "
                    "calculated because no valid "
                    "valuation result is available."
                ),
            )

        normalized_weights = (
            self._resolve_weights(
                results=valid_results,
                weights=weights,
            )
        )

        weighted_results = tuple(
            result
            for result in valid_results
            if normalized_weights.get(
                self._normalize_method(
                    result.method
                ),
                0.0,
            ) > 0
        )

        if not weighted_results:
            return self._create_na_result(
                components=all_results,
                current_price=resolved_price,
                description=(
                    "Weighted fair value cannot be "
                    "calculated because no positive "
                    "valuation weight is available."
                ),
            )

        intrinsic_value = sum(
            self._require_intrinsic_value(
                result
            )
            * normalized_weights[
                self._normalize_method(
                    result.method
                )
            ]
            for result in weighted_results
        )

        (
            upside,
            downside,
            margin_of_safety,
            recommendation,
        ) = self._calculate_market_metrics(
            intrinsic_value=intrinsic_value,
            current_price=resolved_price,
        )

        return WeightedFairValueResult(
            method="WEIGHTED",
            intrinsic_value=intrinsic_value,
            current_price=resolved_price,
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            components=all_results,
            normalized_weights=normalized_weights,
            description=(
                "Weighted fair value calculated from "
                f"{len(weighted_results)} valid "
                "valuation method(s)."
            ),
            source=self._source,
            schema_version=self._schema_version,
        )

    def _prepare_results(
        self,
        results: Iterable[
            ValuationResult
        ],
    ) -> tuple[
        ValuationResult,
        ...,
    ]:
        if results is None:
            raise ValueError(
                "results must not be None"
            )

        prepared_results = tuple(
            results
        )

        for result in prepared_results:
            if result is None:
                raise ValueError(
                    "valuation result must not be None"
                )

            if not isinstance(
                result,
                ValuationResult,
            ):
                raise TypeError(
                    "each result must be a "
                    "ValuationResult"
                )

        self._validate_unique_methods(
            prepared_results
        )

        return prepared_results

    def _get_valid_results(
        self,
        results: tuple[
            ValuationResult,
            ...,
        ],
    ) -> tuple[
        ValuationResult,
        ...,
    ]:
        valid_results: list[
            ValuationResult
        ] = []

        for result in results:
            method = str(
                result.method
            ).strip()

            intrinsic_value = (
                result.intrinsic_value
            )

            if not method:
                continue

            if intrinsic_value is None:
                continue

            if intrinsic_value <= 0:
                continue

            valid_results.append(
                result
            )

        return tuple(
            valid_results
        )

    def _resolve_weights(
        self,
        results: tuple[
            ValuationResult,
            ...,
        ],
        weights: Mapping[
            str,
            float,
        ] | None,
    ) -> dict[
        str,
        float,
    ]:
        methods = tuple(
            self._normalize_method(
                result.method
            )
            for result in results
        )

        if weights is None:
            equal_weight = (
                1.0 / len(methods)
            )

            return {
                method: equal_weight
                for method in methods
            }

        prepared_weights = (
            self._prepare_weights(
                weights
            )
        )

        selected_weights = {
            method: prepared_weights.get(
                method,
                0.0,
            )
            for method in methods
        }

        total_weight = sum(
            selected_weights.values()
        )

        if total_weight <= 0:
            return {}

        return {
            method: weight / total_weight
            for method, weight
            in selected_weights.items()
            if weight > 0
        }

    def _prepare_weights(
        self,
        weights: Mapping[
            str,
            float,
        ],
    ) -> dict[
        str,
        float,
    ]:
        if not isinstance(
            weights,
            Mapping,
        ):
            raise TypeError(
                "weights must be a mapping"
            )

        prepared_weights: dict[
            str,
            float,
        ] = {}

        for method, weight in weights.items():
            normalized_method = (
                self._normalize_method(
                    method
                )
            )

            if isinstance(
                weight,
                bool,
            ):
                raise TypeError(
                    "valuation weight must be numeric"
                )

            if not isinstance(
                weight,
                (int, float),
            ):
                raise TypeError(
                    "valuation weight must be numeric"
                )

            numeric_weight = float(
                weight
            )

            if numeric_weight < 0:
                raise ValueError(
                    "valuation weight must not "
                    "be negative"
                )

            prepared_weights[
                normalized_method
            ] = numeric_weight

        return prepared_weights

    def _resolve_current_price(
        self,
        results: tuple[
            ValuationResult,
            ...,
        ],
        current_price: float | None,
    ) -> float | None:
        if current_price is not None:
            return current_price

        for result in results:
            if result.current_price is not None:
                return result.current_price

        return None

    def _calculate_market_metrics(
        self,
        intrinsic_value: float,
        current_price: float | None,
    ) -> tuple[
        float | None,
        float | None,
        float | None,
        str,
    ]:
        upside = None
        downside = None
        margin_of_safety = None
        recommendation = "N/A"

        if (
            current_price is None
            or current_price <= 0
        ):
            return (
                upside,
                downside,
                margin_of_safety,
                recommendation,
            )

        upside = (
            intrinsic_value - current_price
        ) / current_price

        downside = (
            (
                current_price - intrinsic_value
            )
            / current_price
            if current_price > intrinsic_value
            else 0.0
        )

        margin_of_safety = (
            intrinsic_value - current_price
        ) / intrinsic_value

        if (
            margin_of_safety
            >= self._required_margin_of_safety
        ):
            recommendation = "BUY"

        elif margin_of_safety >= 0:
            recommendation = "WATCH"

        else:
            recommendation = "AVOID"

        return (
            upside,
            downside,
            margin_of_safety,
            recommendation,
        )

    def _create_na_result(
        self,
        components: tuple[
            ValuationResult,
            ...,
        ],
        current_price: float | None,
        description: str,
    ) -> WeightedFairValueResult:
        return WeightedFairValueResult(
            method="WEIGHTED",
            intrinsic_value=None,
            current_price=current_price,
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="N/A",
            components=components,
            normalized_weights={},
            description=description,
            source=self._source,
            schema_version=self._schema_version,
        )

    def _validate_unique_methods(
        self,
        results: tuple[
            ValuationResult,
            ...,
        ],
    ) -> None:
        seen_methods: set[
            str
        ] = set()

        for result in results:
            method = str(
                result.method
            ).strip()

            if not method:
                continue

            normalized_method = (
                self._normalize_method(
                    method
                )
            )

            if normalized_method in seen_methods:
                raise ValueError(
                    "duplicate valuation method: "
                    f"{normalized_method}"
                )

            seen_methods.add(
                normalized_method
            )

    def _require_intrinsic_value(
        self,
        result: ValuationResult,
    ) -> float:
        intrinsic_value = (
            result.intrinsic_value
        )

        if intrinsic_value is None:
            raise RuntimeError(
                "valid valuation result has no "
                "intrinsic value"
            )

        return intrinsic_value

    def _normalize_method(
        self,
        method: str,
    ) -> str:
        return self._normalize_required_text(
            value=method,
            field_name="method",
        ).upper()

    def _normalize_required_text(
        self,
        value: str,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized_value = str(
            value
        ).strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized_value