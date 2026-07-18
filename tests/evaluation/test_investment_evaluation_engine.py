from __future__ import annotations

from dataclasses import dataclass

import pytest

from dmi_core.decision.decision_engine import (
    DecisionEngine,
)
from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.evaluation.investment_evaluation_engine import (
    InvestmentEvaluationEngine,
)
from dmi_core.evaluation.investment_evaluation_result import (
    InvestmentEvaluationResult,
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
from dmi_core.valuation.valuation_engine import (
    ValuationEngine,
)


def create_statement(
    symbol: str = "FPT",
    year: int = 2025,
    quarter: int = 4,
    net_profit: float | None = 250.0,
    equity: float | None = 1_000.0,
    total_debt: float | None = 400.0,
    charter_capital: float | None = 500.0,
    eps: float | None = 4_000.0,
    balance_sheet_symbol: str | None = None,
    income_statement_symbol: str | None = None,
    balance_sheet_year: int | None = None,
    income_statement_year: int | None = None,
    balance_sheet_quarter: int | None = None,
    income_statement_quarter: int | None = None,
) -> FinancialStatement:
    """
    Build a production FinancialStatement for evaluation tests.

    Default financial quality:

        ROE = 250 / 1,000 = 25%
            → Profitability score = 100

        Debt/Equity = 400 / 1,000 = 0.40
            → Leverage score = 100

        Overall financial score = 100

    Default valuation:

        PE fair value:
            4,000 × 10 = 40,000

        PB fair value:
            1,000 / 500 × 10,000 × 1.5
            = 30,000

        Equal weighted fair value:
            (40,000 + 30,000) / 2
            = 35,000
    """

    resolved_balance_symbol = (
        symbol
        if balance_sheet_symbol is None
        else balance_sheet_symbol
    )

    resolved_income_symbol = (
        symbol
        if income_statement_symbol is None
        else income_statement_symbol
    )

    resolved_balance_year = (
        year
        if balance_sheet_year is None
        else balance_sheet_year
    )

    resolved_income_year = (
        year
        if income_statement_year is None
        else income_statement_year
    )

    resolved_balance_quarter = (
        quarter
        if balance_sheet_quarter is None
        else balance_sheet_quarter
    )

    resolved_income_quarter = (
        quarter
        if income_statement_quarter is None
        else income_statement_quarter
    )

    balance_sheet = BalanceSheet(
        symbol=resolved_balance_symbol,
        year=resolved_balance_year,
        quarter=resolved_balance_quarter,
        equity=equity,
        total_debt=total_debt,
        charter_capital=charter_capital,
        total_assets=1_600.0,
    )

    income_statement = IncomeStatement(
        symbol=resolved_income_symbol,
        year=resolved_income_year,
        quarter=resolved_income_quarter,
        net_profit=net_profit,
        revenue=2_000.0,
        gross_profit=600.0,
        eps=eps,
    )

    return FinancialStatement(
        symbol=symbol,
        year=year,
        quarter=quarter,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
    )


def test_engine_can_be_created() -> None:
    engine = InvestmentEvaluationEngine()

    assert engine is not None
    assert isinstance(
        engine.valuation_engine,
        ValuationEngine,
    )
    assert isinstance(
        engine.decision_engine,
        DecisionEngine,
    )
    assert isinstance(
        engine.policy,
        DecisionPolicy,
    )


def test_full_pipeline_returns_investment_result() -> None:
    engine = InvestmentEvaluationEngine()

    result = engine.evaluate(
        statement=create_statement(),
        current_price=25_000.0,
    )

    assert isinstance(
        result,
        InvestmentEvaluationResult,
    )

    assert result.symbol == "FPT"
    assert result.current_price == pytest.approx(
        25_000.0
    )


def test_full_pipeline_calculates_financial_analysis() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=25_000.0,
    )

    assert result.analysis.profitability is not None
    assert result.analysis.leverage is not None

    assert result.analysis.profitability.score == 100
    assert result.analysis.leverage.score == 100

    assert result.financial_score == pytest.approx(
        100.0
    )

    assert result.financial_rating == "A"
    assert result.analysis.recommendation == "BUY"


def test_full_pipeline_calculates_weighted_fair_value() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=25_000.0,
    )

    assert result.valuation.method == "WEIGHTED"

    assert result.intrinsic_value == pytest.approx(
        35_000.0
    )

    assert result.fair_value == pytest.approx(
        35_000.0
    )

    assert result.valuation_component_count == 2

    assert result.valuation.get_weight(
        "PE"
    ) == pytest.approx(0.50)

    assert result.valuation.get_weight(
        "PB"
    ) == pytest.approx(0.50)


def test_full_pipeline_returns_strong_buy() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=25_000.0,
    )

    # Weighted fair value = 35,000
    # Current price = 25,000
    # MOS = 10,000 / 35,000 = 28.57%
    assert result.margin_of_safety == pytest.approx(
        10_000.0 / 35_000.0
    )

    assert result.recommendation == "STRONG BUY"
    assert result.decision.recommendation == "STRONG BUY"
    assert result.stars == 5
    assert 0 <= result.confidence <= 100

    assert result.is_actionable is True
    assert result.is_buy_candidate is True


def test_full_pipeline_uses_custom_valuation_weights() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=25_000.0,
        valuation_weights={
            "PE": 0.80,
            "PB": 0.20,
        },
    )

    # PE = 40,000
    # PB = 30,000
    # Weighted = 40,000 × 0.8 + 30,000 × 0.2
    #          = 38,000
    assert result.intrinsic_value == pytest.approx(
        38_000.0
    )

    assert result.valuation.get_weight(
        "PE"
    ) == pytest.approx(0.80)

    assert result.valuation.get_weight(
        "PB"
    ) == pytest.approx(0.20)

    assert result.recommendation == "STRONG BUY"


def test_pipeline_continues_when_pe_is_unavailable() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(
            eps=None,
        ),
        current_price=20_000.0,
    )

    # PB remains valid:
    # 1,000 / 500 × 10,000 × 1.5 = 30,000
    assert result.intrinsic_value == pytest.approx(
        30_000.0
    )

    assert result.valuation.get_weight(
        "PE"
    ) == pytest.approx(0.0)

    assert result.valuation.get_weight(
        "PB"
    ) == pytest.approx(1.0)

    assert result.valuation_component_count == 1
    assert result.recommendation == "STRONG BUY"


def test_pipeline_continues_when_pb_is_unavailable() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(
            charter_capital=None,
        ),
        current_price=30_000.0,
    )

    # PE remains valid:
    # 4,000 × 10 = 40,000
    assert result.intrinsic_value == pytest.approx(
        40_000.0
    )

    assert result.valuation.get_weight(
        "PE"
    ) == pytest.approx(1.0)

    assert result.valuation.get_weight(
        "PB"
    ) == pytest.approx(0.0)

    assert result.valuation_component_count == 1
    assert result.recommendation == "STRONG BUY"


def test_pipeline_returns_non_actionable_when_all_valuations_invalid() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(
            eps=None,
            charter_capital=None,
        ),
        current_price=20_000.0,
    )

    assert result.intrinsic_value is None
    assert result.margin_of_safety is None
    assert result.valuation_component_count == 0

    # Financial score remains strong, so WatchRule is
    # currently the first matching fallback rule.
    assert result.recommendation == "WATCH"

    assert result.is_actionable is False
    assert result.is_buy_candidate is False


def test_pipeline_returns_buy_for_regular_buy_thresholds() -> None:
    statement = create_statement(
        # ROE = 120 / 1,000 = 12%
        # Profitability score = 60
        net_profit=120.0,
        # Debt/Equity = 400 / 1,000 = 0.40
        # Leverage score = 100
        # Overall score = 80
    )

    result = InvestmentEvaluationEngine().evaluate(
        statement=statement,
        current_price=31_000.0,
    )

    # Weighted fair value = 35,000
    # MOS = 4,000 / 35,000 = 11.43%
    #
    # Overall score = (60 + 100) / 2 = 80
    # MOS < 15% prevents STRONG BUY
    # MOS >= 10% allows BUY
    assert result.financial_score == pytest.approx(
        80.0
    )

    assert result.margin_of_safety == pytest.approx(
        4_000.0 / 35_000.0
    )

    assert result.recommendation == "BUY"
    assert result.stars == 4


def test_pipeline_returns_watch_when_valuation_is_not_attractive() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=34_000.0,
    )

    # MOS = 1,000 / 35,000 = 2.86%
    # Strong financial score but valuation is not cheap enough.
    assert result.margin_of_safety == pytest.approx(
        1_000.0 / 35_000.0
    )

    assert result.recommendation == "WATCH"
    assert result.stars == 3
    assert result.is_buy_candidate is False


def test_pipeline_returns_sell_for_low_financial_quality() -> None:
    statement = create_statement(
        # ROE = 20 / 1,000 = 2%
        # Profitability score = 20
        net_profit=20.0,
        # Debt/Equity = 2,500 / 1,000 = 2.5
        # Leverage score = 20
        total_debt=2_500.0,
    )

    result = InvestmentEvaluationEngine().evaluate(
        statement=statement,
        current_price=45_000.0,
    )

    assert result.financial_score == pytest.approx(
        20.0
    )

    assert result.recommendation == "SELL"
    assert result.stars == 2
    assert result.is_buy_candidate is False


def test_evaluation_can_override_decision_policy() -> None:
    custom_policy = DecisionPolicy(
        min_score_buy=100,
        min_margin_of_safety=0.50,
        min_score_regular_buy=100,
        min_margin_of_safety_buy=0.50,
        min_score_watch=95,
    )

    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=25_000.0,
        policy=custom_policy,
    )

    # Overall score is 100, so WatchRule still matches
    # because min_score_watch is 95.
    #
    # Strong Buy and Buy fail due to MOS threshold of 50%.
    assert result.recommendation == "WATCH"


def test_constructor_dependencies_are_preserved() -> None:
    valuation_engine = ValuationEngine(
        config=ValuationConfig(
            target_pe=12.0,
            target_pb=2.0,
        )
    )

    decision_engine = DecisionEngine()

    policy = DecisionPolicy(
        min_margin_of_safety=0.20,
    )

    engine = InvestmentEvaluationEngine(
        valuation_engine=valuation_engine,
        decision_engine=decision_engine,
        policy=policy,
    )

    assert engine.valuation_engine is valuation_engine
    assert engine.decision_engine is decision_engine
    assert engine.policy is policy


def test_custom_valuation_engine_is_used() -> None:
    valuation_engine = ValuationEngine(
        config=ValuationConfig(
            target_pe=12.0,
            target_pb=2.0,
        )
    )

    engine = InvestmentEvaluationEngine(
        valuation_engine=valuation_engine,
    )

    result = engine.evaluate(
        statement=create_statement(),
        current_price=25_000.0,
    )

    # PE:
    # 4,000 × 12 = 48,000
    #
    # PB:
    # 20,000 BVPS × 2 = 40,000
    #
    # Equal weighted:
    # 44,000
    assert result.intrinsic_value == pytest.approx(
        44_000.0
    )


def test_result_metadata_is_preserved() -> None:
    engine = InvestmentEvaluationEngine(
        source="DMI-EVALUATION",
        schema_version="1.1",
    )

    result = engine.evaluate(
        statement=create_statement(
            symbol="fpt",
        ),
        current_price=25_000.0,
    )

    assert result.symbol == "FPT"
    assert result.source == "DMI-EVALUATION"
    assert result.schema_version == "1.1"


def test_result_explain_contains_pipeline_information() -> None:
    result = InvestmentEvaluationEngine().evaluate(
        statement=create_statement(),
        current_price=25_000.0,
    )

    explanation = result.explain()

    assert "Symbol: FPT" in explanation
    assert "Financial Score: 100.00" in explanation
    assert "Weighted Fair Value: 35,000.00" in explanation
    assert "Current Price: 25,000.00" in explanation
    assert "Margin of Safety: 28.57%" in explanation
    assert "Recommendation: STRONG BUY" in explanation
    assert "Decision: STRONG BUY" in explanation


def test_rejects_none_statement() -> None:
    with pytest.raises(
        ValueError,
        match="statement must not be None",
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=None,
            current_price=25_000.0,
        )


def test_rejects_invalid_statement_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "statement must be a "
            "FinancialStatement"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=object(),
            current_price=25_000.0,
        )


def test_rejects_missing_balance_sheet() -> None:
    statement = FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        balance_sheet=None,
        income_statement=IncomeStatement(
            symbol="FPT",
            year=2025,
            quarter=4,
            net_profit=250.0,
            eps=4_000.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "statement.balance_sheet "
            "must not be None"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=statement,
            current_price=25_000.0,
        )


def test_rejects_missing_income_statement() -> None:
    statement = FinancialStatement(
        symbol="FPT",
        year=2025,
        quarter=4,
        balance_sheet=BalanceSheet(
            symbol="FPT",
            year=2025,
            quarter=4,
            equity=1_000.0,
        ),
        income_statement=None,
    )

    with pytest.raises(
        ValueError,
        match=(
            "statement.income_statement "
            "must not be None"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=statement,
            current_price=25_000.0,
        )


def test_rejects_balance_sheet_symbol_mismatch() -> None:
    statement = create_statement(
        symbol="FPT",
        balance_sheet_symbol="HPG",
    )

    with pytest.raises(
        ValueError,
        match=(
            "balance_sheet.symbol does not "
            "match statement.symbol"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=statement,
            current_price=25_000.0,
        )


def test_rejects_income_statement_symbol_mismatch() -> None:
    statement = create_statement(
        symbol="FPT",
        income_statement_symbol="HPG",
    )

    with pytest.raises(
        ValueError,
        match=(
            "income_statement.symbol does not "
            "match statement.symbol"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=statement,
            current_price=25_000.0,
        )


def test_rejects_balance_sheet_year_mismatch() -> None:
    statement = create_statement(
        year=2025,
        balance_sheet_year=2024,
    )

    with pytest.raises(
        ValueError,
        match=(
            "balance_sheet.year does not "
            "match statement.year"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=statement,
            current_price=25_000.0,
        )


def test_rejects_income_statement_quarter_mismatch() -> None:
    statement = create_statement(
        quarter=4,
        income_statement_quarter=3,
    )

    with pytest.raises(
        ValueError,
        match=(
            "income_statement.quarter does not "
            "match statement.quarter"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=statement,
            current_price=25_000.0,
        )


@pytest.mark.parametrize(
    "current_price",
    [
        0.0,
        -1.0,
    ],
)
def test_rejects_non_positive_current_price(
    current_price: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "current_price must be "
            "greater than zero"
        ),
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=create_statement(),
            current_price=current_price,
        )


@pytest.mark.parametrize(
    "current_price",
    [
        "25000",
        True,
        object(),
    ],
)
def test_rejects_non_numeric_current_price(
    current_price,
) -> None:
    with pytest.raises(
        TypeError,
        match="current_price must be numeric",
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=create_statement(),
            current_price=current_price,
        )


def test_rejects_invalid_policy_override() -> None:
    with pytest.raises(
        TypeError,
        match="policy must be a DecisionPolicy",
    ):
        InvestmentEvaluationEngine().evaluate(
            statement=create_statement(),
            current_price=25_000.0,
            policy=object(),
        )


def test_rejects_empty_engine_source() -> None:
    with pytest.raises(
        ValueError,
        match="source must not be empty",
    ):
        InvestmentEvaluationEngine(
            source="   ",
        )


def test_rejects_empty_schema_version() -> None:
    with pytest.raises(
        ValueError,
        match="schema_version must not be empty",
    ):
        InvestmentEvaluationEngine(
            schema_version="",
        )