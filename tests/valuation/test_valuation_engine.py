from __future__ import annotations

from dataclasses import dataclass

import pytest

from dmi_core.valuation.base_valuation import (
    BaseValuation,
)
from dmi_core.valuation.ev_ebitda_valuation import (
    EVEBITDAValuation,
)
from dmi_core.valuation.pb_valuation import (
    PBValuation,
)
from dmi_core.valuation.pe_valuation import (
    PEValuation,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)
from dmi_core.valuation.valuation_engine import (
    ValuationEngine,
)
from dmi_core.valuation.valuation_registry import (
    ValuationRegistry,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)
from dmi_core.valuation.weighted_fair_value_result import (
    WeightedFairValueResult,
)


@dataclass
class FakeIncomeStatement:
    eps: float | None
    ebitda: float | None = None


@dataclass
class FakeBalanceSheet:
    equity: float | None = 2_000.0
    charter_capital: float | None = 1_000.0
    total_debt: float | None = 1_000.0
    cash: float | None = 500.0


@dataclass
class FakeFinancialStatement:
    income_statement: FakeIncomeStatement
    balance_sheet: FakeBalanceSheet


class SuccessfulFakeValuation(
    BaseValuation
):
    def __init__(
        self,
        statement,
        config=None,
    ) -> None:
        super().__init__(
            statement
        )

        self._config = config

    def evaluate(
        self,
        current_price: float | None = None,
    ) -> ValuationResult:
        return ValuationResult(
            method="FAKE",
            intrinsic_value=100.0,
            current_price=current_price,
            upside=1.0,
            downside=0.0,
            margin_of_safety=0.5,
            recommendation="BUY",
            description="Fake valuation",
        )


class BrokenFakeValuation(
    BaseValuation
):
    def evaluate(
        self,
        current_price: float | None = None,
    ) -> ValuationResult:
        raise RuntimeError(
            "valuation model failed"
        )


def create_statement(
    eps: float | None = 5.0,
    ebitda: float | None = None,
    equity: float | None = 2_000.0,
    charter_capital: float | None = 1_000.0,
    total_debt: float | None = 1_000.0,
    cash: float | None = 500.0,
) -> FakeFinancialStatement:
    return FakeFinancialStatement(
        income_statement=(
            FakeIncomeStatement(
                eps=eps,
                ebitda=ebitda,
            )
        ),
        balance_sheet=(
            FakeBalanceSheet(
                equity=equity,
                charter_capital=charter_capital,
                total_debt=total_debt,
                cash=cash,
            )
        ),
    )


def test_default_engine_uses_all_default_models() -> None:
    engine = ValuationEngine()

    assert engine.available_methods() == (
        "PEValuation",
        "PBValuation",
        "EVEBITDAValuation",
    )


def test_evaluate_default_pe_method() -> None:
    statement = create_statement(
        eps=5.0
    )

    config = ValuationConfig(
        target_pe=10.0,
        required_margin_of_safety=0.25,
    )

    engine = ValuationEngine(
        config=config
    )

    result = engine.evaluate(
        statement=statement,
        current_price=40.0,
    )

    assert result.method == "PE"
    assert result.intrinsic_value == 50.0
    assert result.current_price == 40.0

    assert result.upside == pytest.approx(
        0.25
    )

    assert result.margin_of_safety == (
        pytest.approx(0.20)
    )

    assert result.recommendation == "WATCH"


def test_evaluate_pe_by_short_method_name() -> None:
    engine = ValuationEngine()

    result = engine.evaluate_by_method(
        statement=create_statement(
            eps=5.0
        ),
        method="PE",
        current_price=30.0,
    )

    assert result.method == "PE"
    assert result.intrinsic_value == 50.0


def test_evaluate_pe_by_class_name() -> None:
    engine = ValuationEngine()

    result = engine.evaluate(
        statement=create_statement(
            eps=4.0
        ),
        current_price=20.0,
        method="PEValuation",
    )

    assert result.method == "PE"
    assert result.intrinsic_value == 40.0


def test_evaluate_pb_by_short_method_name() -> None:
    config = ValuationConfig(
        target_pb=1.5,
        required_margin_of_safety=0.25,
    )

    engine = ValuationEngine(
        config=config
    )

    result = engine.evaluate_by_method(
        statement=create_statement(
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
        method="PB",
        current_price=20_000.0,
    )

    assert result.method == "PB"

    assert result.intrinsic_value == (
        pytest.approx(30_000.0)
    )

    assert result.current_price == (
        pytest.approx(20_000.0)
    )

    assert result.upside == pytest.approx(
        0.50
    )

    assert result.margin_of_safety == (
        pytest.approx(1 / 3)
    )

    assert result.recommendation == "BUY"


def test_evaluate_pb_by_class_name() -> None:
    engine = ValuationEngine()

    result = engine.evaluate(
        statement=create_statement(
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
        current_price=25_000.0,
        method="PBValuation",
    )

    assert result.method == "PB"

    assert result.intrinsic_value == (
        pytest.approx(30_000.0)
    )

    assert result.recommendation == "WATCH"


def test_evaluate_ev_ebitda_by_short_method_name() -> None:
    config = ValuationConfig(
        target_ev_ebitda=8.0,
        required_margin_of_safety=0.25,
    )

    engine = ValuationEngine(
        config=config
    )

    result = engine.evaluate_by_method(
        statement=create_statement(
            ebitda=500.0,
            charter_capital=1_000.0,
            total_debt=1_000.0,
            cash=500.0,
        ),
        method="EVEBITDA",
        current_price=25_000.0,
    )

    assert result.method == "EVEBITDA"
    assert result.intrinsic_value == pytest.approx(35_000.0)
    assert result.current_price == pytest.approx(25_000.0)
    assert result.upside == pytest.approx(0.40)
    assert result.margin_of_safety == pytest.approx(
        10_000.0 / 35_000.0
    )
    assert result.recommendation == "BUY"


def test_evaluate_ev_ebitda_by_class_name() -> None:
    engine = ValuationEngine()

    result = engine.evaluate(
        statement=create_statement(
            ebitda=500.0,
            charter_capital=1_000.0,
            total_debt=1_000.0,
            cash=500.0,
        ),
        current_price=31_500.0,
        method="EVEBITDAValuation",
    )

    assert result.method == "EVEBITDA"
    assert result.intrinsic_value == pytest.approx(35_000.0)
    assert result.recommendation == "WATCH"


def test_evaluate_rejects_unknown_method() -> None:
    engine = ValuationEngine()

    with pytest.raises(
        ValueError,
        match=(
            "valuation method is not registered"
        ),
    ):
        engine.evaluate(
            statement=create_statement(),
            method="DCF",
        )


def test_evaluate_rejects_none_statement() -> None:
    engine = ValuationEngine()

    with pytest.raises(
        ValueError,
        match=(
            "statement must not be None"
        ),
    ):
        engine.evaluate(
            statement=None
        )


def test_empty_registry_cannot_evaluate() -> None:
    engine = ValuationEngine(
        registry=ValuationRegistry()
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "valuation registry has no models"
        ),
    ):
        engine.evaluate(
            statement=create_statement()
        )


def test_evaluate_all_default_models_preserves_order() -> None:
    engine = ValuationEngine()

    results = engine.evaluate_all(
        statement=create_statement(
            eps=5.0,
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
        current_price=40.0,
    )

    assert len(results) == 3

    assert results[0].method == "PE"
    assert results[1].method == "PB"
    assert results[2].method == "EVEBITDA"
    assert results[2].intrinsic_value is None
    assert results[2].recommendation == "N/A"


def test_evaluate_all_custom_registry_preserves_order() -> None:
    registry = ValuationRegistry(
        models=[
            PEValuation,
            SuccessfulFakeValuation,
        ]
    )

    engine = ValuationEngine(
        registry=registry
    )

    results = engine.evaluate_all(
        statement=create_statement(
            eps=5.0
        ),
        current_price=40.0,
    )

    assert len(results) == 2

    assert results[0].method == "PE"
    assert results[1].method == "FAKE"


def test_evaluate_all_isolates_model_error() -> None:
    registry = ValuationRegistry(
        models=[
            SuccessfulFakeValuation,
            BrokenFakeValuation,
        ]
    )

    engine = ValuationEngine(
        registry=registry
    )

    results = engine.evaluate_all(
        statement=create_statement(),
        current_price=50.0,
        continue_on_error=True,
    )

    assert len(results) == 2

    assert results[0].recommendation == "BUY"

    assert results[1].method == "BROKENFAKE"
    assert results[1].recommendation == "N/A"
    assert results[1].description is not None

    assert (
        "valuation model failed"
        in results[1].description
    )


def test_evaluate_all_can_raise_model_error() -> None:
    registry = ValuationRegistry(
        models=[
            BrokenFakeValuation,
        ]
    )

    engine = ValuationEngine(
        registry=registry
    )

    with pytest.raises(
        RuntimeError,
        match="valuation model failed",
    ):
        engine.evaluate_all(
            statement=create_statement(),
            continue_on_error=False,
        )


def test_missing_eps_returns_na_result() -> None:
    engine = ValuationEngine()

    result = engine.evaluate(
        statement=create_statement(
            eps=None
        ),
        current_price=20.0,
        method="PE",
    )

    assert result.method == "PE"
    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"
    assert result.upside is None
    assert result.margin_of_safety is None


def test_missing_pb_inputs_return_na_result() -> None:
    engine = ValuationEngine()

    result = engine.evaluate(
        statement=create_statement(
            equity=None,
            charter_capital=1_000.0,
        ),
        current_price=20_000.0,
        method="PB",
    )

    assert result.method == "PB"
    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"
    assert result.upside is None
    assert result.margin_of_safety is None


def test_missing_ev_ebitda_inputs_return_na_result() -> None:
    engine = ValuationEngine()

    result = engine.evaluate(
        statement=create_statement(
            ebitda=None,
        ),
        current_price=20_000.0,
        method="EVEBITDA",
    )

    assert result.method == "EVEBITDA"
    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"
    assert result.upside is None
    assert result.margin_of_safety is None


def test_evaluate_weighted_equal_weights() -> None:
    config = ValuationConfig(
        target_pe=10.0,
        target_pb=1.5,
    )

    engine = ValuationEngine(
        config=config
    )

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=4_000.0,
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
    )

    # PE fair value:
    # 4,000 × 10 = 40,000
    #
    # PB fair value:
    # 2,000 / 1,000 × 10,000 × 1.5 = 30,000
    #
    # Equal weighted fair value:
    # (40,000 + 30,000) / 2 = 35,000

    assert isinstance(
        result,
        WeightedFairValueResult,
    )

    assert result.method == "WEIGHTED"

    assert result.intrinsic_value == (
        pytest.approx(35_000.0)
    )

    assert result.get_weight(
        "PE"
    ) == pytest.approx(0.5)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(0.5)

    assert result.valid_component_count == 2
    assert len(result.components) == 3
    assert result.components[2].method == "EVEBITDA"
    assert result.components[2].intrinsic_value is None


def test_evaluate_weighted_uses_all_three_valid_models() -> None:
    engine = ValuationEngine(
        config=ValuationConfig(
            target_pe=10.0,
            target_pb=1.5,
            target_ev_ebitda=8.0,
        )
    )

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=4_000.0,
            ebitda=500.0,
            equity=2_000.0,
            charter_capital=1_000.0,
            total_debt=1_000.0,
            cash=500.0,
        ),
    )

    assert result.intrinsic_value == pytest.approx(35_000.0)

    assert result.get_weight(
        "PE"
    ) == pytest.approx(1 / 3)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(1 / 3)

    assert result.get_weight(
        "EVEBITDA"
    ) == pytest.approx(1 / 3)

    assert result.valid_component_count == 3
    assert len(result.components) == 3


def test_evaluate_weighted_custom_weights() -> None:
    engine = ValuationEngine(
        config=ValuationConfig(
            target_pe=10.0,
            target_pb=1.5,
        )
    )

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=4_000.0,
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
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

    assert result.get_weight(
        "EVEBITDA"
    ) == pytest.approx(0.0)


def test_evaluate_weighted_with_current_price() -> None:
    engine = ValuationEngine(
        config=ValuationConfig(
            target_pe=10.0,
            target_pb=1.5,
            required_margin_of_safety=0.25,
        )
    )

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=4_000.0,
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
        current_price=25_000.0,
    )

    assert result.intrinsic_value == (
        pytest.approx(35_000.0)
    )

    assert result.current_price == (
        pytest.approx(25_000.0)
    )

    assert result.upside == pytest.approx(
        0.40
    )

    assert result.margin_of_safety == (
        pytest.approx(
            10_000.0 / 35_000.0
        )
    )

    assert result.recommendation == "BUY"


def test_evaluate_weighted_ignores_invalid_pe() -> None:
    engine = ValuationEngine()

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=None,
            equity=2_000.0,
            charter_capital=1_000.0,
        ),
        current_price=20_000.0,
    )

    assert result.intrinsic_value == (
        pytest.approx(30_000.0)
    )

    assert result.get_weight(
        "PE"
    ) == pytest.approx(0.0)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(1.0)

    assert result.valid_component_count == 1
    assert len(result.components) == 3
    assert result.get_weight(
        "EVEBITDA"
    ) == pytest.approx(0.0)
    assert result.recommendation == "BUY"


def test_evaluate_weighted_ignores_invalid_pb() -> None:
    engine = ValuationEngine()

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=4_000.0,
            equity=None,
            charter_capital=1_000.0,
        ),
        current_price=30_000.0,
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

    assert result.valid_component_count == 1

    assert result.get_weight(
        "EVEBITDA"
    ) == pytest.approx(0.0)

    assert len(result.components) == 3


def test_evaluate_weighted_uses_only_ev_ebitda_when_others_invalid() -> None:
    engine = ValuationEngine()

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=None,
            ebitda=500.0,
            equity=None,
            charter_capital=1_000.0,
            total_debt=1_000.0,
            cash=500.0,
        ),
        current_price=25_000.0,
    )

    assert result.intrinsic_value == pytest.approx(35_000.0)

    assert result.get_weight(
        "PE"
    ) == pytest.approx(0.0)

    assert result.get_weight(
        "PB"
    ) == pytest.approx(0.0)

    assert result.get_weight(
        "EVEBITDA"
    ) == pytest.approx(1.0)

    assert result.valid_component_count == 1
    assert len(result.components) == 3
    assert result.recommendation == "BUY"


def test_evaluate_weighted_returns_na_when_all_invalid() -> None:
    engine = ValuationEngine()

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=None,
            equity=None,
            charter_capital=None,
        ),
        current_price=20_000.0,
    )

    assert result.method == "WEIGHTED"
    assert result.intrinsic_value is None
    assert result.current_price == 20_000.0
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"
    assert result.valid_component_count == 0
    assert len(result.components) == 3


def test_evaluate_weighted_preserves_config_metadata() -> None:
    config = ValuationConfig(
        source="DMI-PRODUCTION",
        schema_version="3.1",
    )

    engine = ValuationEngine(
        config=config
    )

    result = engine.evaluate_weighted(
        statement=create_statement(
            eps=4_000.0,
        )
    )

    assert result.source == "DMI-PRODUCTION"
    assert result.schema_version == "3.1"


def test_evaluate_weighted_propagates_error_when_requested() -> None:
    registry = ValuationRegistry(
        models=[
            BrokenFakeValuation,
        ]
    )

    engine = ValuationEngine(
        registry=registry
    )

    with pytest.raises(
        RuntimeError,
        match="valuation model failed",
    ):
        engine.evaluate_weighted(
            statement=create_statement(),
            continue_on_error=False,
        )


def test_evaluate_weighted_isolates_model_error() -> None:
    registry = ValuationRegistry(
        models=[
            SuccessfulFakeValuation,
            BrokenFakeValuation,
        ]
    )

    engine = ValuationEngine(
        registry=registry
    )

    result = engine.evaluate_weighted(
        statement=create_statement(),
        current_price=50.0,
        continue_on_error=True,
    )

    assert result.method == "WEIGHTED"
    assert result.intrinsic_value == pytest.approx(100.0)
    assert result.valid_component_count == 1
    assert len(result.components) == 2
    assert result.get_weight("FAKE") == pytest.approx(1.0)
    assert result.recommendation == "BUY"


def test_engine_exposes_config() -> None:
    config = ValuationConfig(
        target_pe=12.0
    )

    engine = ValuationEngine(
        config=config
    )

    assert engine.config is config


def test_engine_exposes_registry() -> None:
    registry = ValuationRegistry.default()

    engine = ValuationEngine(
        registry=registry
    )

    assert engine.registry is registry