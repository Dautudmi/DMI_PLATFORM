from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class IncomeStatement:
    """
    DMI Standard Income Statement Model.

    Model chuẩn của DMI cho Báo cáo kết quả kinh doanh.
    Không phụ thuộc CafeF hay provider nào.
    """

    # Metadata
    symbol: str
    year: int
    quarter: int
    report_type: Optional[str] = None
    currency: str = "VND"
    unit: str = "Billion"
    provider: Optional[str] = "DMI"
    schema_version: str = "2.0"

    # Revenue & profit
    revenue: Optional[float] = None
    cost_of_goods_sold: Optional[float] = None
    gross_profit: Optional[float] = None

    financial_income: Optional[float] = None
    financial_expense: Optional[float] = None
    selling_expense: Optional[float] = None
    admin_expense: Optional[float] = None

    operating_profit: Optional[float] = None
    other_profit: Optional[float] = None
    pre_tax_profit: Optional[float] = None
    tax_expense: Optional[float] = None
    net_profit: Optional[float] = None

    # Operating metric
    ebitda: Optional[float] = None
    
    # Per share
    eps: Optional[float] = None