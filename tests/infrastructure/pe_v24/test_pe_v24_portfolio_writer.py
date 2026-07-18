from datetime import datetime

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from infrastructure.pe_v24.pe_v24_portfolio_writer import (
    PEV24PortfolioWriter,
)


class FakeClock:
    def now(self):
        return datetime(
            2026,
            7,
            10,
            15,
            30,
            0,
        )


def build_portfolio() -> Portfolio:
    return Portfolio(
        client_name="anh_manh",
        cash=50000000,
        holdings=[
            Holding(
                symbol="NAB",
                quantity=1200,
                average_cost=12.45,
            ),
            Holding(
                symbol="FTS",
                quantity=400,
                average_cost=26.465,
            ),
        ],
    )


def test_pe_v24_portfolio_writer_requires_folder():
    try:
        PEV24PortfolioWriter(
            clients_folder_path=""
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "clients_folder_path must not be empty"
        )
    else:
        assert False


def test_pe_v24_portfolio_writer_writes_new_file(
    tmp_path,
):
    writer = PEV24PortfolioWriter(
        clients_folder_path=str(tmp_path)
    )

    result = writer.write(build_portfolio())

    assert result.success is True
    assert result.client_id == "anh_manh"
    assert result.total_positions == 2
    assert result.backup_path is None
    assert result.error is None

    file_path = (
        tmp_path / "client_anh_manh.csv"
    )

    text = file_path.read_text(
        encoding="utf-8-sig"
    )

    assert (
        "Ticker,Quantity,AverageCost"
        in text
    )
    assert "FTS,400,26.465" in text
    assert "NAB,1200,12.45" in text


def test_pe_v24_portfolio_writer_creates_backup(
    tmp_path,
):
    file_path = (
        tmp_path / "client_anh_manh.csv"
    )

    file_path.write_text(
        "Ticker,Quantity,AverageCost\n"
        "NAB,1000,12.3\n",
        encoding="utf-8-sig",
    )

    writer = PEV24PortfolioWriter(
        clients_folder_path=str(tmp_path),
        clock=FakeClock(),
    )

    result = writer.write(build_portfolio())

    assert result.success is True
    assert result.backup_path is not None

    backup_path = (
        tmp_path
        / "_portfolio_backups"
        / "anh_manh"
        / "client_anh_manh_20260710_153000_000000.csv"
    )

    assert backup_path.exists()

    backup_text = backup_path.read_text(
        encoding="utf-8-sig"
    )

    assert "NAB,1000,12.3" in backup_text


def test_pe_v24_portfolio_writer_rejects_duplicate_symbols(
    tmp_path,
):
    portfolio = Portfolio(
        client_name="anh_manh",
        holdings=[
            Holding(
                symbol="NAB",
                quantity=100,
                average_cost=12,
            ),
            Holding(
                symbol="nab",
                quantity=200,
                average_cost=13,
            ),
        ],
    )

    writer = PEV24PortfolioWriter(
        clients_folder_path=str(tmp_path)
    )

    result = writer.write(portfolio)

    assert result.success is False
    assert result.total_positions == 0
    assert result.error == (
        "duplicate holding symbol: NAB"
    )


def test_pe_v24_portfolio_writer_rejects_zero_quantity(
    tmp_path,
):
    portfolio = Portfolio(
        client_name="anh_manh",
        holdings=[
            Holding(
                symbol="NAB",
                quantity=0,
                average_cost=12,
            )
        ],
    )

    writer = PEV24PortfolioWriter(
        clients_folder_path=str(tmp_path)
    )

    result = writer.write(portfolio)

    assert result.success is False
    assert result.error == (
        "holding quantity must be greater "
        "than 0 for symbol NAB"
    )


def test_pe_v24_portfolio_writer_sorts_symbols(
    tmp_path,
):
    portfolio = Portfolio(
        client_name="anh_manh",
        holdings=[
            Holding(
                symbol="NAB",
                quantity=100,
                average_cost=12,
            ),
            Holding(
                symbol="FPT",
                quantity=200,
                average_cost=90,
            ),
        ],
    )

    writer = PEV24PortfolioWriter(
        clients_folder_path=str(tmp_path)
    )

    result = writer.write(portfolio)

    assert result.success is True

    lines = (
        tmp_path / "client_anh_manh.csv"
    ).read_text(
        encoding="utf-8-sig"
    ).splitlines()

    assert lines[1].startswith("FPT,")
    assert lines[2].startswith("NAB,")