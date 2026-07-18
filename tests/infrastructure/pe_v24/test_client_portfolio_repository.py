from infrastructure.pe_v24.client_portfolio_repository import (
    PEV24ClientPortfolioRepository,
)


def test_client_portfolio_repository_builds_correct_path(
    tmp_path,
):
    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    expected = tmp_path / "client_anh_manh.csv"

    assert repository.get_portfolio_path(
        "anh_manh"
    ) == str(expected)


def test_client_portfolio_repository_loads_quantity_and_cost(
    tmp_path,
):
    file_path = tmp_path / "client_anh_manh.csv"

    file_path.write_text(
        "Ticker,Quantity,Cost\n"
        "NAB,1000,12.300\n"
        "FTS,500,26.465\n"
        "CTS,800,25.500\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    positions = repository.load_portfolio(
        "anh_manh"
    )

    assert len(positions) == 3

    assert positions[0].ticker == "NAB"
    assert positions[0].symbol == "NAB"
    assert positions[0].quantity == 1000
    assert positions[0].cost == 12.3
    assert positions[0].average_cost == 12.3

    assert positions[1].ticker == "FTS"
    assert positions[1].quantity == 500
    assert positions[1].cost == 26.465

    assert positions[2].ticker == "CTS"
    assert positions[2].quantity == 800
    assert positions[2].cost == 25.5


def test_client_portfolio_repository_load_symbols(
    tmp_path,
):
    file_path = tmp_path / "client_anh_manh.csv"

    file_path.write_text(
        "Ticker,Quantity,Cost\n"
        "NAB,1000,12.300\n"
        "FTS,500,26.465\n"
        "NAB,200,12.500\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    assert repository.load_symbols(
        "anh_manh"
    ) == [
        "NAB",
        "FTS",
    ]


def test_client_portfolio_repository_rejects_missing_quantity(
    tmp_path,
):
    file_path = tmp_path / "client_anh_manh.csv"

    file_path.write_text(
        "Ticker,Cost\n"
        "NAB,12.300\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    try:
        repository.load_portfolio("anh_manh")
    except ValueError as exc:
        assert (
            str(exc)
            == "Missing Quantity for ticker NAB at row 2"
        )
    else:
        assert False


def test_client_portfolio_repository_rejects_zero_quantity(
    tmp_path,
):
    file_path = tmp_path / "client_anh_manh.csv"

    file_path.write_text(
        "Ticker,Quantity,Cost\n"
        "NAB,0,12.300\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    try:
        repository.load_portfolio("anh_manh")
    except ValueError as exc:
        assert (
            str(exc)
            == "Quantity must be greater than 0 "
            "for ticker NAB at row 2"
        )
    else:
        assert False


def test_client_portfolio_repository_rejects_missing_cost(
    tmp_path,
):
    file_path = tmp_path / "client_anh_manh.csv"

    file_path.write_text(
        "Ticker,Quantity,Cost\n"
        "NAB,1000,\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    try:
        repository.load_portfolio("anh_manh")
    except ValueError as exc:
        assert (
            str(exc)
            == "Missing Cost for ticker NAB at row 2"
        )
    else:
        assert False


def test_client_portfolio_repository_rejects_invalid_client_id(
    tmp_path,
):
    repository = PEV24ClientPortfolioRepository(
        clients_folder_path=str(tmp_path)
    )

    try:
        repository.get_portfolio_path("../secret")
    except ValueError as exc:
        assert (
            str(exc)
            == "client_id contains invalid path characters"
        )
    else:
        assert False