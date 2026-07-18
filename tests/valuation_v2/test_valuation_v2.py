from __future__ import annotations

import pytest

from dmi_core.market.market_data import (
    MarketData,
)
from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
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
from dmi_core.valuation_v2.ev_ebitda_valuation import (
    EVEBITDAValuationV2,
)
from dmi_core.valuation_v2.pb_valuation import (
    PBValuationV2,
)
from dmi_core.valuation_v2.pe_valuation import (
    PEValuationV2,
)
from dmi_core.valuation_v2.valuation_engine import (
    ValuationEngineV2,
)
from dmi_core.valuation_v2.valuation_registry import (
    ValuationRegistryV2,
)
from dmi_core.valuation_v2.weighted_valuation import (
    WeightedValuationV2,
)


@pytest.fixture
def valuation_config() -> ValuationConfig:
    return ValuationConfig(
        target_pe=10.0,
        target_pb=1.5,
        target_ev_ebitda=8.0,
        required_margin_of_safety=0.25,
    )


@pytest.fixture
def financial_statement() -> FinancialStatement:
    balance_sheet = BalanceSheet(
        symbol="FPT",
        year=2025,
        quarter=4,
        cash=100.0,
        short_term_debt=40.0,
        long_term_debt=60.0,
        total_debt=100.0,
        equity=1_000.0,
    )

    income_statement = IncomeStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        net_profit=100.0,
        operating_profit=110.0,
        ebitda=120.0,
        eps=10.0,
    )

    return FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
    )


@pytest.fixture
def market_data() -> MarketData:
    return MarketData(
        symbol="FPT",
        current_price=100.0,
        previous_close=98.0,
        shares_outstanding=1_000_000_000,
        provider="TEST",
    )


class SuccessfulValuationV2(
    BaseValuationV2
):
    method = "SUCCESS"

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:
        self.validate_inputs(
            statement=statement,
            market=market,
        )

        return self.create_result(
            intrinsic_value=150.0,
            current_price=market.current_price,
            description="Successful dummy valuation.",
        )


class FailedValuationV2(
    BaseValuationV2
):
    method = "FAILED"

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:
        raise RuntimeError(
            "dummy valuation failed"
        )


class InvalidResultValuationV2(
    BaseValuationV2
):
    method = "INVALID"

    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ):
        return None


def test_registry_default_contains_three_models():
    registry = ValuationRegistryV2.default()

    assert len(registry) == 3

    assert registry.model_names() == (
        "PEValuationV2",
        "PBValuationV2",
        "EVEBITDAValuationV2",
    )


def test_registry_register_and_unregister():
    registry = ValuationRegistryV2()

    registry.register(
        SuccessfulValuationV2
    )

    assert len(registry) == 1
    assert registry.contains(
        SuccessfulValuationV2
    )

    registry.unregister(
        SuccessfulValuationV2
    )

    assert len(registry) == 0


def test_registry_rejects_duplicate_model():
    registry = ValuationRegistryV2(
        models=[
            SuccessfulValuationV2,
        ]
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            SuccessfulValuationV2
        )


def test_registry_rejects_non_v2_model():
    class InvalidModel:
        pass

    registry = ValuationRegistryV2()

    with pytest.raises(
        TypeError,
        match="must inherit BaseValuationV2",
    ):
        registry.register(
            InvalidModel
        )


def test_pe_valuation_uses_direct_eps(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    model = PEValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert result.method == "PE"
    assert result.intrinsic_value == pytest.approx(
        100.0
    )
    assert result.current_price == pytest.approx(
        100.0
    )
    assert result.upside == pytest.approx(
        0.0
    )
    assert result.margin_of_safety == pytest.approx(
        0.0
    )
    assert result.recommendation == "SELL"


def test_pe_valuation_derives_eps_from_profit_and_shares(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    assert (
        financial_statement.income_statement
        is not None
    )

    financial_statement.income_statement.eps = None
    financial_statement.income_statement.net_profit = (
        100.0
    )

    market_data.shares_outstanding = 1_000_000_000

    model = PEValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert result.intrinsic_value == pytest.approx(
        1_000.0
    )


def test_pe_returns_na_when_eps_is_unavailable(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    assert (
        financial_statement.income_statement
        is not None
    )

    financial_statement.income_statement.eps = None
    financial_statement.income_statement.net_profit = (
        None
    )

    model = PEValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_pb_valuation_derives_bvps(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    model = PBValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    expected_bvps = 1_000.0

    expected_intrinsic_value = (
        expected_bvps
        * 1.5
    )

    assert result.method == "PB"
    assert result.intrinsic_value == pytest.approx(
        expected_intrinsic_value
    )
    assert result.intrinsic_value == pytest.approx(
        1_500.0
    )
    assert result.recommendation == "BUY"


def test_pb_returns_na_without_equity(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    assert (
        financial_statement.balance_sheet
        is not None
    )

    financial_statement.balance_sheet.equity = None

    model = PBValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_ev_ebitda_valuation(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    model = EVEBITDAValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    expected_target_ev = (
        120.0
        * 8.0
    )

    expected_net_debt = (
        100.0
        - 100.0
    )

    expected_equity_value = (
        expected_target_ev
        - expected_net_debt
    )

    expected_intrinsic_value = (
        expected_equity_value
        * 1_000_000_000
        / 1_000_000_000
    )

    assert result.method == "EV/EBITDA"

    assert result.intrinsic_value == pytest.approx(
        expected_intrinsic_value
    )

    


def test_ev_ebitda_uses_net_debt(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    assert (
        financial_statement.balance_sheet
        is not None
    )

    financial_statement.balance_sheet.cash = 20.0
    financial_statement.balance_sheet.total_debt = (
        100.0
    )

    model = EVEBITDAValuationV2(
        config=valuation_config
    )

    result = model.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    expected_target_ev = (
        120.0
        * 8.0
    )

    expected_net_debt = (
        100.0
        - 20.0
    )

    expected_intrinsic_value = (
        (
            expected_target_ev
            - expected_net_debt
        )
        * 1_000_000_000
        / 1_000_000_000
    )

    

    assert result.intrinsic_value == pytest.approx(
        expected_intrinsic_value
    )


def test_engine_runs_all_default_models(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    engine = ValuationEngineV2(
        config=valuation_config
    )

    result = engine.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert result.symbol == "FPT"
    assert result.succeeded
    assert not result.has_errors

    assert result.methods == (
        "PE",
        "PB",
        "EV/EBITDA",
    )

    assert len(
        result.results
    ) == 3

    assert len(
        result.available_results
    ) == 3


def test_engine_evaluate_single_model(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    engine = ValuationEngineV2(
        config=valuation_config
    )

    result = engine.evaluate_model(
        statement=financial_statement,
        market=market_data,
        model_type=PEValuationV2,
    )

    assert result.method == "PE"
    assert result.intrinsic_value == pytest.approx(
        100.0
    )


def test_engine_continues_after_model_error(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    registry = ValuationRegistryV2(
        models=[
            SuccessfulValuationV2,
            FailedValuationV2,
        ]
    )

    engine = ValuationEngineV2(
        registry=registry,
        config=valuation_config,
        continue_on_error=True,
    )

    result = engine.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert len(
        result.results
    ) == 1

    assert len(
        result.errors
    ) == 1

    assert result.has_errors

    assert (
        result.errors[0].model_name
        == "FailedValuationV2"
    )

    assert (
        result.errors[0].exception_type
        == "RuntimeError"
    )


def test_engine_raises_when_continue_on_error_is_false(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    registry = ValuationRegistryV2(
        models=[
            FailedValuationV2,
        ]
    )

    engine = ValuationEngineV2(
        registry=registry,
        config=valuation_config,
        continue_on_error=False,
    )

    with pytest.raises(
        RuntimeError,
        match="dummy valuation failed",
    ):
        engine.evaluate(
            statement=financial_statement,
            market=market_data,
        )


def test_engine_rejects_invalid_model_result(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    registry = ValuationRegistryV2(
        models=[
            InvalidResultValuationV2,
        ]
    )

    engine = ValuationEngineV2(
        registry=registry,
        config=valuation_config,
        continue_on_error=True,
    )

    result = engine.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    assert len(
        result.results
    ) == 0

    assert len(
        result.errors
    ) == 1

    assert (
        result.errors[0].exception_type
        == "ValueError"
    )


def test_engine_rejects_symbol_mismatch(
    financial_statement: FinancialStatement,
    market_data: MarketData,
):
    market_data.symbol = "HPG"

    engine = ValuationEngineV2()

    with pytest.raises(
        ValueError,
        match="must be identical",
    ):
        engine.evaluate(
            statement=financial_statement,
            market=market_data,
        )


def test_weighted_valuation_uses_default_weights(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    engine = ValuationEngineV2(
        config=valuation_config
    )

    engine_result = engine.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    weighted_model = WeightedValuationV2(
        required_margin_of_safety=0.25
    )

    result = weighted_model.evaluate(
        engine_result=engine_result
    )

    expected_fair_value = (
        100.0 * 0.40
        + 1_500.0 * 0.30
        + 960.0 * 0.30
    )

    assert result.succeeded

    assert result.weighted_fair_value == (
        pytest.approx(
            expected_fair_value
        )
    )

    assert result.weighted_fair_value == pytest.approx(
        778.0
    )
    

    assert result.current_price == pytest.approx(
        100.0
    )

    assert result.included_methods == (
        "PE",
        "PB",
        "EV/EBITDA",
    )

    assert result.applied_weights == {
        "PE": pytest.approx(
            0.40
        ),
        "PB": pytest.approx(
            0.30
        ),
        "EV/EBITDA": pytest.approx(
            0.30
        ),
    }


def test_weighted_valuation_normalizes_remaining_weights(
    financial_statement: FinancialStatement,
    market_data: MarketData,
    valuation_config: ValuationConfig,
):
    assert (
        financial_statement.income_statement
        is not None
    )

    financial_statement.income_statement.ebitda = None
    financial_statement.income_statement.operating_profit = (
        None
    )

    engine = ValuationEngineV2(
        config=valuation_config
    )

    engine_result = engine.evaluate(
        statement=financial_statement,
        market=market_data,
    )

    weighted_model = WeightedValuationV2()

    result = weighted_model.evaluate(
        engine_result=engine_result
    )

    expected_pe_weight = (
        0.40
        / 0.70
    )

    expected_pb_weight = (
        0.30
        / 0.70
    )

    expected_fair_value = (
        100.0 * expected_pe_weight
        + 1_500.0 * expected_pb_weight
    )

    assert result.weighted_fair_value == (
        pytest.approx(
            expected_fair_value
        )
    )

    assert result.applied_weights[
        "PE"
    ] == pytest.approx(
        expected_pe_weight
    )

    assert result.applied_weights[
        "PB"
    ] == pytest.approx(
        expected_pb_weight
    )

    assert result.excluded_methods == (
        "EV/EBITDA",
    )


def test_weighted_valuation_returns_na_without_results():
    registry = ValuationRegistryV2(
        models=[]
    )

    engine = ValuationEngineV2(
        registry=registry
    )

    statement = FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
    )

    market = MarketData(
        symbol="FPT",
        current_price=100.0,
        provider="TEST",
    )

    engine_result = engine.evaluate(
        statement=statement,
        market=market,
    )

    weighted_model = WeightedValuationV2()

    result = weighted_model.evaluate(
        engine_result=engine_result
    )

    assert not result.succeeded
    assert result.weighted_fair_value is None
    assert result.recommendation == "N/A"
    assert result.applied_weights == {}


def test_weighted_valuation_rejects_negative_weight():
    with pytest.raises(
        ValueError,
        match="must not be negative",
    ):
        WeightedValuationV2(
            weights={
                "PE": 0.50,
                "PB": -0.20,
            }
        )


def test_weighted_valuation_rejects_zero_total_weight():
    with pytest.raises(
        ValueError,
        match="total weight must be greater than zero",
    ):
        WeightedValuationV2(
            weights={
                "PE": 0.0,
                "PB": 0.0,
            }
        )