from dmi_core.models.income_statement import IncomeStatement


def test_create_income_statement():
    income = IncomeStatement(
        symbol="AAA",
        year=2026,
        quarter=1,
        revenue=1000,
        net_profit=100,
        eps=1500,
    )

    assert income.symbol == "AAA"
    assert income.year == 2026
    assert income.quarter == 1
    assert income.revenue == 1000
    assert income.net_profit == 100
    assert income.eps == 1500


if __name__ == "__main__":
    income = IncomeStatement(
        symbol="AAA",
        year=2026,
        quarter=1,
        revenue=1000,
        net_profit=100,
        eps=1500,
    )

    print(income)