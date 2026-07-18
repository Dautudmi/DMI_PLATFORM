from apps.shared.pipeline import Pipeline
from apps.shared.pipeline import PipelineContext
from apps.shared.pipeline import PipelineStage


class AddMetadataStage(PipelineStage):
    def run(self, context: PipelineContext) -> PipelineContext:
        context.metadata["stage"] = "completed"
        return context


class AddErrorStage(PipelineStage):
    def run(self, context: PipelineContext) -> PipelineContext:
        context.errors.append("test error")
        return context


def test_pipeline_executes_stage():
    pipeline = Pipeline(stages=[AddMetadataStage()])
    context = PipelineContext()

    result = pipeline.execute(context)

    assert result.success is True
    assert result.context.metadata["stage"] == "completed"


def test_pipeline_result_fails_when_context_has_errors():
    pipeline = Pipeline(stages=[AddErrorStage()])
    context = PipelineContext()

    result = pipeline.execute(context)

    assert result.success is False
    assert result.context.errors == ["test error"]


def test_pipeline_executes_stages_in_order():
    class FirstStage(PipelineStage):
        def run(self, context: PipelineContext) -> PipelineContext:
            context.metadata["order"] = ["first"]
            return context

    class SecondStage(PipelineStage):
        def run(self, context: PipelineContext) -> PipelineContext:
            context.metadata["order"].append("second")
            return context

    pipeline = Pipeline(stages=[FirstStage(), SecondStage()])
    context = PipelineContext()

    result = pipeline.execute(context)

    assert result.context.metadata["order"] == ["first", "second"]


def test_pipeline_rejects_invalid_context():
    pipeline = Pipeline(stages=[])

    try:
        pipeline.execute("not a context")
    except TypeError as exc:
        assert "PipelineContext" in str(exc)
    else:
        assert False