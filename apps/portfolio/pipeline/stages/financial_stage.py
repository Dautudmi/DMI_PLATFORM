from apps.portfolio.pipeline.holding_context import HoldingPipelineContext
from apps.portfolio.providers.financial_data_provider import FinancialDataProvider
from apps.portfolio.providers.null_financial_data_provider import NullFinancialDataProvider
from apps.shared.pipeline.context import PipelineContext
from apps.shared.pipeline.stage import PipelineStage


class FinancialStage(PipelineStage):
    """
    Pipeline stage that loads financial statement data for a holding.
    """

    def __init__(
        self,
        financial_provider: FinancialDataProvider | None = None,
    ) -> None:
        self._financial_provider = financial_provider or NullFinancialDataProvider()

    def run(self, context: PipelineContext) -> PipelineContext:
        if not isinstance(context, HoldingPipelineContext):
            raise TypeError("FinancialStage expects a HoldingPipelineContext instance")

        if context.holding is None:
            context.errors.append("Missing holding")
            return context

        context.financial_statement = self._financial_provider.get_statement(
            context.holding.symbol
        )

        return context