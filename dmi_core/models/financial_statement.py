from dataclasses import dataclass
from typing import Optional

from dmi_core.models.balance_sheet import BalanceSheet
from dmi_core.models.income_statement import IncomeStatement


@dataclass(slots=True)
class FinancialStatement:
    """
    DMI Standard Financial Statement Aggregate.

    Đây là Aggregate Root của Financial Domain.
    Mọi Engine sau này nên nhận FinancialStatement,
    không làm việc trực tiếp với raw dict từ provider.
    """

    symbol: str
    year: int
    quarter: int

    balance_sheet: Optional[BalanceSheet] = None
    income_statement: Optional[IncomeStatement] = None

    report_type: Optional[str] = None
    currency: str = "VND"
    unit: str = "Billion"
    provider: Optional[str] = "DMI"
    schema_version: str = "2.0"