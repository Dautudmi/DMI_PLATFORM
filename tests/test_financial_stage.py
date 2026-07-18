from apps.portfolio.models.holding import Holding
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.pipeline.stages.financial_stage import FinancialStage
from apps.portfolio.providers.mock_financial_data_provider import (
    MockFinancialDataProvider,
)


def test_financial_stage_loads_statement_when_available():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    statement = object()

    provider = MockFinancialDataProvider(
        statements={
            "FPT": statement,
        }
    )

    context = HoldingPipelineContext(holding=holding)
    stage = FinancialStage(financial_provider=provider)

    result = stage.run(context)

    assert result.financial_statement is statement
    assert result.errors == []


def test_financial_stage_returns_none_when_statement_missing():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    provider = MockFinancialDataProvider()

    context = HoldingPipelineContext(holding=holding)
    stage = FinancialStage(financial_provider=provider)

    result = stage.run(context)

    assert result.financial_statement is None
    assert result.errors == []


def test_financial_stage_adds_error_when_holding_missing():
    context = HoldingPipelineContext()

    stage = FinancialStage()
    result = stage.run(context)

    assert result.financial_statement is None
    assert result.errors == ["Missing holding"]


def test_financial_stage_rejects_invalid_context():
    stage = FinancialStage()

    try:
        stage.run("not a context")
    except TypeError as exc:
        assert "HoldingPipelineContext" in str(exc)
    else:
        assert False