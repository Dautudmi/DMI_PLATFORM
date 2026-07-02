from dmi_core.services import FinancialStatementService


def test_pipeline():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    assert statement is not None

    assert statement.balance_sheet is not None

    assert statement.income_statement is not None

    print("=" * 60)

    print("SYMBOL:", statement.symbol)

    print("YEAR:", statement.year)

    print("QUARTER:", statement.quarter)

    print("-" * 60)

    print("TOTAL ASSETS:",
          statement.balance_sheet.total_assets)

    print("EQUITY:",
          statement.balance_sheet.equity)

    print("REVENUE:",
          statement.income_statement.revenue)

    print("NET PROFIT:",
          statement.income_statement.net_profit)

    print("=" * 60)


if __name__ == "__main__":
    test_pipeline()