from dataclasses import dataclass

from infrastructure.pe_v24.pe_v24_client_data_service import (
    PEV24ClientDataService,
)


@dataclass(frozen=True)
class FakeClientConfig:
    client_id: str
    capital: float
    cash_percent: float


@dataclass(frozen=True)
class FakePosition:
    ticker: str
    cost: float


class FakeClientRegistryRepository:
    def require_by_id(self, client_id: str):
        return FakeClientConfig(
            client_id=client_id,
            capital=300000000,
            cash_percent=0,
        )


class FakeClientPortfolioRepository:
    def load_portfolio(self, client_id: str):
        return [
            FakePosition(ticker="NAB", cost=12.3),
            FakePosition(ticker="FTS", cost=26.465),
        ]


def test_client_data_service_requires_registry_repository():
    try:
        PEV24ClientDataService(
            client_registry_repository=None,
            client_portfolio_repository=(
                FakeClientPortfolioRepository()
            ),
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "client_registry_repository must not be None"
        )
    else:
        assert False


def test_client_data_service_requires_portfolio_repository():
    try:
        PEV24ClientDataService(
            client_registry_repository=(
                FakeClientRegistryRepository()
            ),
            client_portfolio_repository=None,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "client_portfolio_repository must not be None"
        )
    else:
        assert False


def test_client_data_service_loads_client_data():
    service = PEV24ClientDataService(
        client_registry_repository=(
            FakeClientRegistryRepository()
        ),
        client_portfolio_repository=(
            FakeClientPortfolioRepository()
        ),
    )

    result = service.load_client_data("anh_manh")

    assert result.success is True
    assert result.client_id == "anh_manh"
    assert result.client_config.capital == 300000000
    assert result.total_positions == 2
    assert result.positions[0].ticker == "NAB"
    assert result.error is None


def test_client_data_service_returns_failed_result():
    class FailingRegistryRepository:
        def require_by_id(self, client_id: str):
            raise KeyError(f"Client not found: {client_id}")

    service = PEV24ClientDataService(
        client_registry_repository=(
            FailingRegistryRepository()
        ),
        client_portfolio_repository=(
            FakeClientPortfolioRepository()
        ),
    )

    result = service.load_client_data("missing")

    assert result.success is False
    assert result.client_id == "missing"
    assert result.client_config is None
    assert result.positions is None
    assert result.total_positions == 0
    assert "Client not found: missing" in result.error