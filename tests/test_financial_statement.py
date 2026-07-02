from dmi_core.models.balance_sheet import BalanceSheet
from dmi_core.models.income_statement import IncomeStatement
from dmi_core.models.financial_statement import FinancialStatement


def test_create_financial_statement():
    bs = BalanceSheet(
        symbol="AAA",
        year=2026,
        quarter=1,
        total_assets=1000,
        equity=400,
    )

    income = IncomeStatement(
        symbol="AAA",
        year=2026,
        quarter=1,
        revenue=800,
        net_profit=100,
    )

    fs = FinancialStatement(
        symbol="AAA",
        year=2026,
        quarter=1,
        balance_sheet=bs,
        income_statement=income,
    )

    assert fs.symbol == "AAA"
    assert fs.balance_sheet.total_assets == 1000
    assert fs.balance_sheet.equity == 400
    assert fs.income_statement.revenue == 800
    assert fs.income_statement.net_profit == 100


if __name__ == "__main__":
    bs = BalanceSheet(
        symbol="AAA",
        year=2026,
        quarter=1,
        total_assets=1000,
        equity=400,
    )

    income = IncomeStatement(
        symbol="AAA",
        year=2026,
        quarter=1,
        revenue=800,
        net_profit=100,
    )

    fs = FinancialStatement(
        symbol="AAA",
        year=2026,
        quarter=1,
        balance_sheet=bs,
        income_statement=income,
    )

    print(fs)