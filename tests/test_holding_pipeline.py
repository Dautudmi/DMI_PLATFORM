from apps.portfolio.models.holding import Holding
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.pipeline.holding_pipeline import HoldingPipeline
from apps.portfolio.providers.mock_financial_data_provider import (
    MockFinancialDataProvider,
)


class FakeDMIService:
    def analyze(self, statement, current_price=None):
        return {
            "statement": statement,
            "current_price": current_price,
        }


def test_holding_pipeline_runs_all_stages_successfully():
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

    pipeline = HoldingPipeline(
        financial_provider=provider,
        dmi_service=FakeDMIService(),
    )

    context = HoldingPipelineContext(holding=holding)

    result = pipeline.execute(context)

    assert result.success is True
    assert result.context.position.market_value == 10000000
    assert result.context.financial_statement is statement
    assert result.context.dmi_report["statement"] is statement
    assert result.context.dmi_report["current_price"] == 100000


def test_holding_pipeline_fails_when_holding_missing():
    pipeline = HoldingPipeline(
        dmi_service=FakeDMIService(),
    )

    context = HoldingPipelineContext()

    result = pipeline.execute(context)

    assert result.success is False
    assert "Missing holding" in result.context.errors


def test_holding_pipeline_fails_when_financial_statement_missing():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    pipeline = HoldingPipeline(
        financial_provider=MockFinancialDataProvider(),
        dmi_service=FakeDMIService(),
    )

    context = HoldingPipelineContext(holding=holding)

    result = pipeline.execute(context)

    assert result.success is False
    assert "Missing financial statement" in result.context.errors