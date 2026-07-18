from apps.portfolio.providers.financial_data_provider import (
    FinancialDataProvider,
)
from apps.portfolio.providers.null_financial_data_provider import (
    NullFinancialDataProvider,
)


def test_null_provider_is_provider():
    provider = NullFinancialDataProvider()

    assert isinstance(provider, FinancialDataProvider)


def test_null_provider_returns_none():
    provider = NullFinancialDataProvider()

    assert provider.get_statement("FPT") is None