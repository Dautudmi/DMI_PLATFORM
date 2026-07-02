import requests

from dmi_core.providers.base_provider import BaseProvider


class CafeFProvider(BaseProvider):
    BASE_URL = "https://msh-appdata.cafef.vn/rest-api/api/v1/FinanceReports"

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://s.cafef.vn/"
    }

    def _get_report(self, symbol: str, period: str, report_type: str, page_size: int = 4):
        symbol = symbol.upper()
        period = period.upper()

        url = f"{self.BASE_URL}/{symbol}/{period}/{report_type}?pageIndex=1&pageSize={page_size}"

        response = requests.get(url, headers=self.HEADERS, timeout=20)

        if response.status_code != 200:
            raise Exception(f"CafeF API error {response.status_code}: {url}")

        data = response.json()

        if not data.get("succeeded"):
            raise Exception(f"CafeF API failed: {url}")

        return data

    def get_balance_sheet(self, symbol: str, period: str = "NAM", page_size: int = 4):
        return self._get_report(symbol, period, "BSHEET", page_size)

    def get_income_statement(self, symbol: str, period: str = "NAM", page_size: int = 4):
        return self._get_report(symbol, period, "INSTA", page_size)