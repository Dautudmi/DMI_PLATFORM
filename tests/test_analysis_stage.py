from apps.portfolio.models.holding import Holding
from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.pipeline.stages.analysis_stage import AnalysisStage


class FakeDMIService:
    def __init__(self):
        self.called = False

    def analyze(self, statement, current_price=None):
        self.called = True
        return {
            "statement": statement,
            "current_price": current_price,
        }


def test_analysis_stage_creates_dmi_report():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    statement = object()
    service = FakeDMIService()

    context = HoldingPipelineContext(
        holding=holding,
        financial_statement=statement,
    )

    stage = AnalysisStage(dmi_service=service)
    result = stage.run(context)

    assert service.called is True
    assert result.dmi_report["statement"] is statement
    assert result.dmi_report["current_price"] == 100000
    assert result.errors == []


def test_analysis_stage_adds_error_when_holding_missing():
    context = HoldingPipelineContext(
        financial_statement=object(),
    )

    stage = AnalysisStage(dmi_service=FakeDMIService())
    result = stage.run(context)

    assert result.dmi_report is None
    assert result.errors == ["Missing holding"]


def test_analysis_stage_adds_error_when_statement_missing():
    holding = Holding(
        symbol="FPT",
        quantity=100,
        average_cost=80000,
        current_price=100000,
    )

    context = HoldingPipelineContext(holding=holding)

    stage = AnalysisStage(dmi_service=FakeDMIService())
    result = stage.run(context)

    assert result.dmi_report is None
    assert result.errors == ["Missing financial statement"]


def test_analysis_stage_rejects_invalid_context():
    stage = AnalysisStage(dmi_service=FakeDMIService())

    try:
        stage.run("not a context")
    except TypeError as exc:
        assert "HoldingPipelineContext" in str(exc)
    else:
        assert False