from apps.portfolio.providers.financial_data_provider import FinancialDataProvider
from apps.portfolio.providers.mock_financial_data_provider import (
    MockFinancialDataProvider,
)


def test_mock_financial_data_provider_is_financial_data_provider():
    provider = MockFinancialDataProvider()

    assert isinstance(provider, FinancialDataProvider)


def test_mock_financial_data_provider_returns_none_when_missing():
    provider = MockFinancialDataProvider()

    result = provider.get_statement("FPT")

    assert result is None