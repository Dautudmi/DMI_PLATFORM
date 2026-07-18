from apps.portfolio.models.holding import Holding
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.pipeline.stages.position_stage import PositionStage
from apps.portfolio.models.position_analysis import PositionAnalysis


def test_position_stage_calculates_position():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    context = HoldingPipelineContext(holding=holding)

    stage = PositionStage()
    result = stage.run(context)

    assert isinstance(result, HoldingPipelineContext)
    assert isinstance(result.position, PositionAnalysis)
    assert result.position.market_value == 10000000
    assert result.position.cost_value == 8000000
    assert result.errors == []


def test_position_stage_adds_error_when_holding_missing():
    context = HoldingPipelineContext()

    stage = PositionStage()
    result = stage.run(context)

    assert result.position is None
    assert result.errors == ["Missing holding"]


def test_position_stage_rejects_invalid_context():
    stage = PositionStage()

    try:
        stage.run("not a context")
    except TypeError as exc:
        assert "HoldingPipelineContext" in str(exc)
    else:
        assert False