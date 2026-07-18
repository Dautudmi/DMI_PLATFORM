from apps.portfolio.factories import HoldingAnalysisFactory
from apps.portfolio.models.holding import Holding
from apps.portfolio.models.position_analysis import PositionAnalysis
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.shared.pipeline.result import PipelineResult


def test_factory_builds_holding_analysis():

    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    context = HoldingPipelineContext(
        holding=holding,
        position=PositionAnalysis(
            market_value=10000000,
            cost_value=8000000,
            unrealized_pnl=2000000,
            unrealized_return=0.25,
        ),
    )

    context.dmi_report = object()

    result = PipelineResult(context=context)

    analysis = HoldingAnalysisFactory.from_pipeline(result)

    assert analysis.symbol == "FPT"
    assert analysis.position.market_value == 10000000
    assert analysis.dmi_report is context.dmi_report