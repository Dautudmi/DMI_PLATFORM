from apps.portfolio.providers.null_financial_data_provider import NullFinancialDataProvider
from apps.portfolio.services.dmi_service import DMIService
from apps.portfolio.services.holding_analyzer import HoldingAnalyzer
from apps.portfolio.services.portfolio_analyzer import PortfolioAnalyzer
from apps.portfolio.services.position_analyzer import PositionAnalyzer
from apps.shared.containers import ApplicationContainer
from apps.shared.containers.providers import ProviderContainer
from apps.shared.containers.services import ServiceContainer


def test_provider_container_creates_default_financial_provider():
    container = ProviderContainer()

    assert isinstance(container.financial_provider, NullFinancialDataProvider)


def test_service_container_creates_services():
    provider = NullFinancialDataProvider()

    container = ServiceContainer(
        financial_provider=provider,
    )

    assert isinstance(container.position_analyzer, PositionAnalyzer)
    assert isinstance(container.dmi_service, DMIService)
    assert isinstance(container.holding_analyzer, HoldingAnalyzer)
    assert isinstance(container.portfolio_analyzer, PortfolioAnalyzer)


def test_application_container_composes_subcontainers():
    container = ApplicationContainer()

    assert isinstance(container.providers, ProviderContainer)
    assert isinstance(container.services, ServiceContainer)


def test_application_container_keeps_backward_compatible_shortcuts():
    container = ApplicationContainer()

    assert isinstance(container.position_analyzer, PositionAnalyzer)
    assert isinstance(container.dmi_service, DMIService)
    assert isinstance(container.holding_analyzer, HoldingAnalyzer)
    assert isinstance(container.portfolio_analyzer, PortfolioAnalyzer)