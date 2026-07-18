from __future__ import annotations

from dataclasses import dataclass

import pytest

from dmi_core.market.market_data import MarketData
from dmi_core.models.balance_sheet import BalanceSheet
from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.models.income_statement import IncomeStatement
from dmi_core.valuation.valuation_engine_v2 import (
    ValuationEngineV2,
)
from dmi_core.valuation.valuation_registry import (
    ValuationRegistry,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


@dataclass
class DummyValuation:
    """
    Fake valuation model for engine testing.
    """

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:

        return ValuationResult(
            method="DUMMY",
            intrinsic_value=100.0,
            current_price=market.current_price,
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="BUY",
            description="Dummy valuation",
            source="TEST",
            schema_version="1.0",
        )


@dataclass
class FailedValuation:

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:

        raise RuntimeError(
            "Dummy Error"
        )


@pytest.fixture
def financial_statement():

    return FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,

        balance_sheet=BalanceSheet(
            symbol="FPT",
            year=2025,
            quarter=4,
        ),

        income_statement=IncomeStatement(
            symbol="FPT",
            year=2025,
            quarter=4,
        ),
    )


@pytest.fixture
def market_data():

    return MarketData(
        symbol="FPT",
        current_price=120000,
    )


def test_available_methods():

    registry = ValuationRegistry()

    registry.register(
        DummyValuation
    )

    engine = ValuationEngineV2(
        registry=registry,
    )

    assert engine.available_methods() == (
        "DummyValuation",
    )


def test_single_evaluation(
    financial_statement,
    market_data,
):

    registry = ValuationRegistry()

    registry.register(
        DummyValuation
    )

    engine = ValuationEngineV2(
        registry=registry,
    )

    result = engine.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert result.method == "DUMMY"

    assert result.intrinsic_value == 100.0


def test_evaluate_all(
    financial_statement,
    market_data,
):

    registry = ValuationRegistry()

    registry.register(
        DummyValuation
    )

    engine = ValuationEngineV2(
        registry=registry,
    )

    results = engine.evaluate_all(
        statement=financial_statement,
        market=market_data,
    )

    assert len(results) == 1

    assert results[0].method == "DUMMY"


def test_continue_on_error(
    financial_statement,
    market_data,
):

    registry = ValuationRegistry()

    registry.register(
        FailedValuation
    )

    engine = ValuationEngineV2(
        registry=registry,
    )

    results = engine.evaluate_all(
        statement=financial_statement,
        market=market_data,
        continue_on_error=True,
    )

    assert len(results) == 1

    assert results[0].recommendation == "N/A"


def test_raise_on_error(
    financial_statement,
    market_data,
):

    registry = ValuationRegistry()

    registry.register(
        FailedValuation
    )

    engine = ValuationEngineV2(
        registry=registry,
    )

    with pytest.raises(
        RuntimeError
    ):

        engine.evaluate_all(
            statement=financial_statement,
            market=market_data,
            continue_on_error=False,
        )