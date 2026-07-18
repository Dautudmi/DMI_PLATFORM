from __future__ import annotations

import pytest

from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation.weighted_fair_value import (
    WeightedFairValueEngine,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


def create_result(
    method: str,
    intrinsic_value: float | None,
    current_price: float | None = None,
) -> ValuationResult:
    return ValuationResult(
        method=method,
        intrinsic_value=intrinsic_value,
        current_price=current_price,
        upside=None,
        downside=None,
        margin_of_safety=None,
        recommendation="N/A",
        description=(
            f"{method} valuation"
        ),
    )


def test_equal_weight_fair_value() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ]
    )

    assert isinstance(
        result,
        WeightedFairValueResult,
    )

    assert result.method == "WEIGHTED"

    assert result.intrinsic_value == (
        pytest.approx(35_000.0)
    )

    assert result.fair_value == (
        pytest.approx(35_000.0)
    )

    assert result.get_weight(
        "PE"
    ) == pytest.approx(0.5)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(0.5)

    assert result.valid_component_count == 2


def test_custom_weights_are_normalized() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        weights={
            "PE": 70.0,
            "PB": 30.0,
        },
    )

    assert result.intrinsic_value == (
        pytest.approx(37_000.0)
    )

    assert result.get_weight(
        "PE"
    ) == pytest.approx(0.70)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(0.30)


def test_method_names_are_case_insensitive() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        weights={
            "pe": 3.0,
            "pb": 1.0,
        },
    )

    assert result.intrinsic_value == (
        pytest.approx(37_500.0)
    )

    assert result.get_weight(
        "pe"
    ) == pytest.approx(0.75)


def test_invalid_component_is_ignored() -> None:
    engine = WeightedFairValueEngine()

    invalid_pb = create_result(
        method="PB",
        intrinsic_value=None,
    )

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            invalid_pb,
        ]
    )

    assert result.intrinsic_value == (
        pytest.approx(40_000.0)
    )

    assert result.get_weight(
        "PE"
    ) == pytest.approx(1.0)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(0.0)

    assert len(result.components) == 2
    assert result.valid_component_count == 1


def test_non_positive_intrinsic_value_is_ignored() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=0.0,
            ),
        ]
    )

    assert result.intrinsic_value == (
        pytest.approx(40_000.0)
    )

    assert result.valid_component_count == 1


def test_no_valid_result_returns_na() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=None,
            ),
            create_result(
                method="PB",
                intrinsic_value=-1.0,
            ),
        ],
        current_price=20_000.0,
    )

    assert result.method == "WEIGHTED"
    assert result.intrinsic_value is None
    assert result.current_price == 20_000.0
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"
    assert result.normalized_weights == {}


def test_current_price_produces_buy() -> None:
    engine = WeightedFairValueEngine(
        required_margin_of_safety=0.25,
    )

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        current_price=25_000.0,
    )

    assert result.intrinsic_value == (
        pytest.approx(35_000.0)
    )

    assert result.upside == pytest.approx(
        0.40
    )

    assert result.downside == pytest.approx(
        0.0
    )

    assert result.margin_of_safety == (
        pytest.approx(
            10_000.0 / 35_000.0
        )
    )

    assert result.recommendation == "BUY"


def test_current_price_produces_watch() -> None:
    engine = WeightedFairValueEngine(
        required_margin_of_safety=0.25,
    )

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        current_price=32_000.0,
    )

    assert result.margin_of_safety == (
        pytest.approx(
            3_000.0 / 35_000.0
        )
    )

    assert result.recommendation == "WATCH"


def test_current_price_produces_avoid() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        current_price=42_000.0,
    )

    assert result.upside == pytest.approx(
        -7_000.0 / 42_000.0
    )

    assert result.downside == pytest.approx(
        7_000.0 / 42_000.0
    )

    assert result.margin_of_safety == (
        pytest.approx(-0.20)
    )

    assert result.recommendation == "AVOID"


def test_price_is_inherited_from_component() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
                current_price=25_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
                current_price=25_000.0,
            ),
        ]
    )

    assert result.current_price == (
        pytest.approx(25_000.0)
    )

    assert result.recommendation == "BUY"


def test_explicit_price_has_priority() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
                current_price=25_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
                current_price=25_000.0,
            ),
        ],
        current_price=32_000.0,
    )

    assert result.current_price == (
        pytest.approx(32_000.0)
    )

    assert result.recommendation == "WATCH"


def test_zero_weight_excludes_method() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        weights={
            "PE": 1.0,
            "PB": 0.0,
        },
    )

    assert result.intrinsic_value == (
        pytest.approx(40_000.0)
    )

    assert result.get_weight(
        "PE"
    ) == pytest.approx(1.0)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(0.0)


def test_all_zero_weights_return_na() -> None:
    engine = WeightedFairValueEngine()

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
            create_result(
                method="PB",
                intrinsic_value=30_000.0,
            ),
        ],
        weights={
            "PE": 0.0,
            "PB": 0.0,
        },
    )

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"
    assert result.normalized_weights == {}


def test_negative_weight_is_rejected() -> None:
    engine = WeightedFairValueEngine()

    with pytest.raises(
        ValueError,
        match=(
            "valuation weight must not be negative"
        ),
    ):
        engine.aggregate(
            results=[
                create_result(
                    method="PE",
                    intrinsic_value=40_000.0,
                ),
            ],
            weights={
                "PE": -1.0,
            },
        )


def test_non_numeric_weight_is_rejected() -> None:
    engine = WeightedFairValueEngine()

    with pytest.raises(
        TypeError,
        match=(
            "valuation weight must be numeric"
        ),
    ):
        engine.aggregate(
            results=[
                create_result(
                    method="PE",
                    intrinsic_value=40_000.0,
                ),
            ],
            weights={
                "PE": "high",
            },
        )


def test_duplicate_methods_are_rejected() -> None:
    engine = WeightedFairValueEngine()

    with pytest.raises(
        ValueError,
        match=(
            "duplicate valuation method: PE"
        ),
    ):
        engine.aggregate(
            results=[
                create_result(
                    method="PE",
                    intrinsic_value=40_000.0,
                ),
                create_result(
                    method="pe",
                    intrinsic_value=30_000.0,
                ),
            ]
        )


def test_none_results_are_rejected() -> None:
    engine = WeightedFairValueEngine()

    with pytest.raises(
        ValueError,
        match="results must not be None",
    ):
        engine.aggregate(
            results=None
        )


def test_invalid_result_type_is_rejected() -> None:
    engine = WeightedFairValueEngine()

    with pytest.raises(
        TypeError,
        match=(
            "each result must be a ValuationResult"
        ),
    ):
        engine.aggregate(
            results=[
                object(),
            ]
        )


def test_negative_required_margin_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "required_margin_of_safety "
            "must not be negative"
        ),
    ):
        WeightedFairValueEngine(
            required_margin_of_safety=-0.01,
        )


def test_source_and_schema_are_preserved() -> None:
    engine = WeightedFairValueEngine(
        source="DMI-WEIGHTED",
        schema_version="3.1",
    )

    result = engine.aggregate(
        results=[
            create_result(
                method="PE",
                intrinsic_value=40_000.0,
            ),
        ]
    )

    assert result.source == "DMI-WEIGHTED"
    assert result.schema_version == "3.1"