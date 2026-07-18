from pathlib import Path

from apps.portfolio.loaders import ClientPortfolioLoader


def test_client_portfolio_loader(tmp_path: Path):

    csv = tmp_path / "client.csv"

    csv.write_text(
        """Client Name,Demo
Cash,10000000

Symbol,Quantity,Average Cost,Current Price
FPT,100,90000,100000
MBB,200,25000,27000
""",
        encoding="utf-8",
    )

    portfolio = ClientPortfolioLoader().load(csv)

    assert portfolio.client_name == "Demo"

    assert portfolio.cash == 10000000

    assert len(portfolio.holdings) == 2

    assert portfolio.holdings[0].symbol == "FPT"

    assert portfolio.holdings[1].symbol == "MBB"