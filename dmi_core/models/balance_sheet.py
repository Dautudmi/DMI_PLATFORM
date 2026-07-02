from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class BalanceSheet:
    """
    DMI Standard Balance Sheet Model.

    Đây là model chuẩn của DMI cho Bảng cân đối kế toán.
    Không phụ thuộc vào CafeF hay bất kỳ provider nào.
    """

    symbol: str
    year: int
    quarter: int
    report_type: Optional[str] = None

    # Assets
    cash: Optional[float] = None
    short_term_investments: Optional[float] = None
    receivables: Optional[float] = None
    inventory: Optional[float] = None
    current_assets: Optional[float] = None
    fixed_assets: Optional[float] = None
    long_term_assets: Optional[float] = None
    total_assets: Optional[float] = None

    # Liabilities
    short_term_debt: Optional[float] = None
    long_term_debt: Optional[float] = None
    total_debt: Optional[float] = None
    total_liabilities: Optional[float] = None

    # Equity
    equity: Optional[float] = None
    charter_capital: Optional[float] = None
    retained_earnings: Optional[float] = None

    # Metadata
    provider: Optional[str] = "DMI"
    currency: str = "VND"
    unit: str = "Billion"
    schema_version: str = "2.0"