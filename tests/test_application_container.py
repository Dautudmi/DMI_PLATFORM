from apps.portfolio.providers.financial_data_provider import (
    FinancialDataProvider,
)
from apps.portfolio.providers.null_financial_data_provider import (
    NullFinancialDataProvider,
)
from apps.portfolio.services.holding_analyzer import HoldingAnalyzer
from apps.portfolio.services.portfolio_analyzer import PortfolioAnalyzer
from apps.portfolio.services.position_analyzer import PositionAnalyzer
from apps.shared.container import ApplicationContainer


def test_application_container_creates_default_services():
    container = ApplicationContainer()

    assert isinstance(container.financial_provider, FinancialDataProvider)
    assert isinstance(container.financial_provider, NullFinancialDataProvider)

    assert isinstance(container.position_analyzer, PositionAnalyzer)
    assert isinstance(container.holding_analyzer, HoldingAnalyzer)
    assert isinstance(container.portfolio_analyzer, PortfolioAnalyzer)


def test_application_container_accepts_custom_financial_provider():
    provider = NullFinancialDataProvider()

    container = ApplicationContainer(
        financial_provider=provider,
    )

    assert container.financial_provider is provider