from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class FinancialField:
    """
    DMI Financial Field Definition.

    Đây là định nghĩa chuẩn cho một chỉ tiêu tài chính trong DMI.
    """

    code: str
    statement: str
    category: str
    cafef_name: str
    cafef_code: Optional[str] = None
    description: Optional[str] = None
    required: bool = False


BALANCE_SHEET_FIELDS = {
    "cash": FinancialField(
        code="cash",
        statement="balance_sheet",
        category="asset",
        cafef_name="Tiền và tương đương tiền",
        description="Cash and cash equivalents",
    ),
    "current_assets": FinancialField(
        code="current_assets",
        statement="balance_sheet",
        category="asset",
        cafef_name="Tổng tài sản lưu động ngắn hạn",
        description="Current assets",
        required=True,
    ),
    "receivables": FinancialField(
        code="receivables",
        statement="balance_sheet",
        category="asset",
        cafef_name="Các khoản phải thu ngắn hạn",
        description="Short-term receivables",
    ),
    "inventory": FinancialField(
        code="inventory",
        statement="balance_sheet",
        category="asset",
        cafef_name="Hàng tồn kho",
        description="Inventory",
    ),
    "total_assets": FinancialField(
        code="total_assets",
        statement="balance_sheet",
        category="asset",
        cafef_name="Tổng tài sản",
        description="Total assets",
        required=True,
    ),
    "current_liabilities": FinancialField(
        code="current_liabilities",
        statement="balance_sheet",
        category="liability",
        cafef_name="Nợ ngắn hạn",
        description="Current liabilities",
    ),
    "total_debt": FinancialField(
        code="total_debt",
        statement="balance_sheet",
        category="liability",
        cafef_name="Tổng nợ",
        description="Total debt",
    ),
    "equity": FinancialField(
        code="equity",
        statement="balance_sheet",
        category="equity",
        cafef_name="Vốn chủ sở hữu",
        description="Owner equity",
        required=True,
    ),
}


INCOME_STATEMENT_FIELDS = {
    "revenue": FinancialField(
        code="revenue",
        statement="income_statement",
        category="revenue",
        cafef_name="Doanh thu bán hàng và CCDV",
        description="Net revenue",
        required=True,
    ),
    "cost_of_goods_sold": FinancialField(
        code="cost_of_goods_sold",
        statement="income_statement",
        category="expense",
        cafef_name="Giá vốn hàng bán",
        description="Cost of goods sold",
    ),
    "gross_profit": FinancialField(
        code="gross_profit",
        statement="income_statement",
        category="profit",
        cafef_name="Lợi nhuận gộp về BH và CCDV",
        description="Gross profit",
    ),
    "profit_before_tax": FinancialField(
        code="profit_before_tax",
        statement="income_statement",
        category="profit",
        cafef_name="Tổng lợi nhuận trước thuế",
        description="Profit before tax",
    ),
    "net_profit": FinancialField(
        code="net_profit",
        statement="income_statement",
        category="profit",
        cafef_name="Lợi nhuận sau thuế",
        description="Net profit",
        required=True,
    ),
    "net_profit_parent": FinancialField(
        code="net_profit_parent",
        statement="income_statement",
        category="profit",
        cafef_name="Lợi nhuận sau thuế của công ty mẹ",
        description="Net profit attributable to parent company",
    ),
}


DMI_FINANCIAL_FIELDS = {
    **BALANCE_SHEET_FIELDS,
    **INCOME_STATEMENT_FIELDS,
}


CAFEF_NAME_TO_DMI_CODE = {
    field.cafef_name: field.code
    for field in DMI_FINANCIAL_FIELDS.values()
}