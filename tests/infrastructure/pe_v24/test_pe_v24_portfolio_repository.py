from infrastructure.pe_v24.portfolio_repository import PEV24PortfolioRepository


def test_pe_v24_portfolio_repository_load_holdings(tmp_path):
    file_path = tmp_path / "portfolio.csv"

    file_path.write_text(
        "client_id,symbol,quantity,cost_price\n"
        "anh_dung,FPT,100,90\n"
        "anh_dung,HPG,200,25\n",
        encoding="utf-8-sig",
    )

    repo = PEV24PortfolioRepository(csv_path=str(file_path))

    holdings = repo.load_holdings()

    assert len(holdings) == 2
    assert holdings[0].client_id == "anh_dung"
    assert holdings[0].symbol == "FPT"
    assert holdings[0].quantity == 100
    assert holdings[0].cost_price == 90


def test_pe_v24_portfolio_repository_load_by_client_id(tmp_path):
    file_path = tmp_path / "portfolio.csv"

    file_path.write_text(
        "client_id,symbol,quantity,cost_price\n"
        "anh_dung,FPT,100,90\n"
        "chi_lan,HPG,200,25\n",
        encoding="utf-8-sig",
    )

    repo = PEV24PortfolioRepository(csv_path=str(file_path))

    holdings = repo.load_by_client_id("anh_dung")

    assert len(holdings) == 1
    assert holdings[0].symbol == "FPT"


def test_pe_v24_portfolio_repository_rejects_empty_client_id(tmp_path):
    file_path = tmp_path / "portfolio.csv"

    file_path.write_text(
        "client_id,symbol,quantity,cost_price\n"
        "anh_dung,FPT,100,90\n",
        encoding="utf-8-sig",
    )

    repo = PEV24PortfolioRepository(csv_path=str(file_path))

    try:
        repo.load_by_client_id("")
    except ValueError as exc:
        assert str(exc) == "client_id must not be empty"
    else:
        assert False