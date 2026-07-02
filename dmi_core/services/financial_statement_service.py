from dmi_core.providers.cafef_provider import CafeFProvider
from dmi_core.parsers.cafef_parser import CafeFParser
from dmi_core.mappers.cafef_mapper import CafeFMapper
from dmi_core.models.financial_statement import FinancialStatement


class FinancialStatementService:
    """
    Service lấy và chuẩn hóa báo cáo tài chính.

    Đây là cửa vào duy nhất để các Engine lấy FinancialStatement.
    Engine không gọi trực tiếp Provider / Parser / Mapper.
    """

    def __init__(self, provider: CafeFProvider | None = None):
        self.provider = provider or CafeFProvider()

    def get(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ) -> FinancialStatement | None:
        """
        Lấy FinancialStatement chuẩn DMI cho một mã cổ phiếu.
        """

        raw_balance = self.provider.get_balance_sheet(
            symbol=symbol,
            period=period,
            page_size=page_size,
        )

        raw_income = self.provider.get_income_statement(
            symbol=symbol,
            period=period,
            page_size=page_size,
        )

        balance_df = CafeFParser.parse_finance_report(raw_balance)
        income_df = CafeFParser.parse_finance_report(raw_income)

        balance_df = CafeFMapper.normalize_finance_df(balance_df)
        income_df = CafeFMapper.normalize_finance_df(income_df)

        return CafeFMapper.to_financial_statement(
            balance_df=balance_df,
            income_df=income_df,
        )