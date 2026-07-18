from apps.portfolio.factories import HoldingAnalysisFactory
from apps.portfolio.models.holding import Holding
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.services.holding_analyzer import HoldingAnalyzer


class FakePipeline:
    def execute(self, context):
        assert isinstance(context, HoldingPipelineContext)

        context.position = object()
        context.dmi_report = object()

        class Result:
            def __init__(self, ctx):
                self.context = ctx

        return Result(context)


class FakeFactory:
    @staticmethod
    def from_pipeline(result):
        return "analysis-result"


def test_holding_analyzer_uses_pipeline(monkeypatch):
    analyzer = HoldingAnalyzer(
        pipeline=FakePipeline(),
    )

    monkeypatch.setattr(
        HoldingAnalysisFactory,
        "from_pipeline",
        FakeFactory.from_pipeline,
    )

    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    result = analyzer.analyze(holding)

    assert result == "analysis-result"


def test_holding_analyzer_rejects_invalid_input():
    analyzer = HoldingAnalyzer(
        pipeline=FakePipeline(),
    )

    try:
        analyzer.analyze("not a holding")
    except TypeError as exc:
        assert "Holding" in str(exc)
    else:
        assert False