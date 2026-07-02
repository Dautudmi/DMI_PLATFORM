"""
DMI Platform Example

Financial Statement Example
"""

from dmi_core.services import FinancialStatementService


def main():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    print("=" * 60)
    print("DMI PLATFORM")
    print("=" * 60)

    print(f"Symbol   : {statement.symbol}")
    print(f"Year     : {statement.year}")
    print(f"Quarter  : {statement.quarter}")

    print("-" * 60)

    print("BALANCE SHEET")

    print(f"Total Assets : {statement.balance_sheet.total_assets}")
    print(f"Equity       : {statement.balance_sheet.equity}")
    print(f"Debt         : {statement.balance_sheet.total_debt}")

    print("-" * 60)

    print("INCOME STATEMENT")

    print(f"Revenue      : {statement.income_statement.revenue}")
    print(f"Gross Profit : {statement.income_statement.gross_profit}")
    print(f"Net Profit   : {statement.income_statement.net_profit}")

    print("=" * 60)


if __name__ == "__main__":
    main()