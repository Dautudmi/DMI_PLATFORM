from apps.portfolio.pipeline.holding_pipeline import HoldingPipeline
from apps.portfolio.providers.financial_data_provider import FinancialDataProvider
from apps.portfolio.services.dmi_service import DMIService
from apps.portfolio.services.holding_analyzer import HoldingAnalyzer
from apps.portfolio.services.portfolio_analyzer import PortfolioAnalyzer
from apps.portfolio.services.position_analyzer import PositionAnalyzer


class ServiceContainer:
    def __init__(
        self,
        financial_provider: FinancialDataProvider,
    ) -> None:
        self.position_analyzer = PositionAnalyzer()

        self.dmi_service = DMIService()

        self.holding_pipeline = HoldingPipeline(
            position_analyzer=self.position_analyzer,
            financial_provider=financial_provider,
            dmi_service=self.dmi_service,
        )

        self.holding_analyzer = HoldingAnalyzer(
            pipeline=self.holding_pipeline,
        )

        self.portfolio_analyzer = PortfolioAnalyzer()