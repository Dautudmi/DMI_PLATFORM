from apps.portfolio.services import PortfolioLoader


def test_portfolio_loader():

    portfolio = PortfolioLoader.from_csv(
        file_path="tests/sample_portfolio.csv",
        client_name="Nguyen Duc Manh",
        cash=25000000,
    )

    assert portfolio.client_name == "Nguyen Duc Manh"
    assert portfolio.cash == 25000000
    assert len(portfolio.holdings) == 3
    assert portfolio.holdings[0].symbol == "AAA"

    print(portfolio)


if __name__ == "__main__":
    test_portfolio_loader()