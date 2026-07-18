from apps.portfolio.models.holding import Holding
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.shared.pipeline.context import PipelineContext


def test_holding_pipeline_context_is_pipeline_context():
    context = HoldingPipelineContext()

    assert isinstance(context, PipelineContext)


def test_holding_pipeline_context_stores_holding():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    context = HoldingPipelineContext(holding=holding)

    assert context.holding == holding
    assert context.holding.symbol == "FPT"


def test_holding_pipeline_context_defaults_are_none():
    context = HoldingPipelineContext()

    assert context.holding is None
    assert context.position is None
    assert context.financial_statement is None
    assert context.dmi_report is None
  

def test_holding_pipeline_context_inherits_metadata_and_errors():
    context = HoldingPipelineContext()

    context.metadata["source"] = "test"
    context.errors.append("sample error")

    assert context.metadata["source"] == "test"
    assert context.errors == ["sample error"]