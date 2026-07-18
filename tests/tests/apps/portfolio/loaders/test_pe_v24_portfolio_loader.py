from infrastructure.pe_v24.pe_v24_client_config import (
    PEV24ClientConfig,
)
from infrastructure.pe_v24.pe_v24_client_position import (
    PEV24ClientPosition,
)
from apps.portfolio.loaders.pe_v24_portfolio_loader import (
    PEV24PortfolioLoader,
)


def test_pe_v24_portfolio_loader_builds_domain_portfolio():
    loader = PEV24PortfolioLoader()

    client_config = PEV24ClientConfig(
        client_id="anh_manh",
        capital=300000000,
        cash_percent=0.2,
    )

    positions = [
        PEV24ClientPosition(
            ticker="NAB",
            quantity=1000,
            cost=12.3,
        ),
        PEV24ClientPosition(
            ticker="FTS",
            quantity=500,
            cost=26.465,
        ),
    ]

    portfolio = loader.load(
        client_config=client_config,
        positions=positions,
    )

    assert portfolio.client_name == "anh_manh"
    assert portfolio.cash == 60000000
    assert len(portfolio.holdings) == 2

    assert portfolio.holdings[0].symbol == "NAB"
    assert portfolio.holdings[0].quantity == 1000
    assert portfolio.holdings[0].average_cost == 12.3
    assert portfolio.holdings[0].current_price is None

    assert portfolio.holdings[1].symbol == "FTS"
    assert portfolio.holdings[1].quantity == 500
    assert portfolio.holdings[1].average_cost == 26.465


def test_pe_v24_portfolio_loader_supports_zero_cash_percent():
    loader = PEV24PortfolioLoader()

    portfolio = loader.load(
        client_config=PEV24ClientConfig(
            client_id="anh_manh",
            capital=300000000,
            cash_percent=0,
        ),
        positions=[],
    )

    assert portfolio.client_name == "anh_manh"
    assert portfolio.cash == 0
    assert portfolio.holdings == []


def test_pe_v24_portfolio_loader_rejects_none_client_config():
    loader = PEV24PortfolioLoader()

    try:
        loader.load(
            client_config=None,
            positions=[],
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "client_config must not be None"
        )
    else:
        assert False


def test_pe_v24_portfolio_loader_rejects_none_positions():
    loader = PEV24PortfolioLoader()

    client_config = PEV24ClientConfig(
        client_id="anh_manh",
        capital=300000000,
        cash_percent=0,
    )

    try:
        loader.load(
            client_config=client_config,
            positions=None,
        )
    except ValueError as exc:
        assert str(exc) == "positions must not be None"
    else:
        assert False


def test_pe_v24_portfolio_loader_rejects_invalid_cash_percent():
    loader = PEV24PortfolioLoader()

    client_config = PEV24ClientConfig(
        client_id="anh_manh",
        capital=300000000,
        cash_percent=1.5,
    )

    try:
        loader.load(
            client_config=client_config,
            positions=[],
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "client_config.cash_percent must be "
            "between 0 and 1"
        )
    else:
        assert False


def test_pe_v24_portfolio_loader_rejects_invalid_quantity():
    loader = PEV24PortfolioLoader()

    client_config = PEV24ClientConfig(
        client_id="anh_manh",
        capital=300000000,
        cash_percent=0,
    )

    positions = [
        PEV24ClientPosition(
            ticker="NAB",
            quantity=0,
            cost=12.3,
        )
    ]

    try:
        loader.load(
            client_config=client_config,
            positions=positions,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "position quantity must be greater than 0 "
            "for symbol NAB"
        )
    else:
        assert False