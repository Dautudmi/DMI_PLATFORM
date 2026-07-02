from dmi_core.services.financial_statement_service import FinancialStatementService


def test_financial_statement_service():
    service = FinancialStatementService()

    statement = service.get("AAA", period="QUY", page_size=4)

    assert statement is not None
    assert statement.symbol == "AAA"
    assert statement.balance_sheet is not None
    assert statement.income_statement is not None

    print(statement)


if __name__ == "__main__":
    test_financial_statement_service()