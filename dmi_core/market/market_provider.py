from __future__ import annotations

from abc import ABC, abstractmethod

from dmi_core.market.market_data import (
    MarketData,
)


class MarketProvider(
    ABC
):
    """
    Abstract provider for stock market data.

    Responsibility:
    - lấy dữ liệu thị trường cho một mã cổ phiếu
    - trả về MarketData chuẩn của DMI

    Provider implementations có thể là:
    - CafeFMarketProvider
    - TCBSMarketProvider
    - SSI Market Provider
    - Internal Market Provider

    Provider không:
    - phân tích tài chính
    - định giá doanh nghiệp
    - đưa ra quyết định đầu tư
    """

    @abstractmethod
    def get(
        self,
        symbol: str,
    ) -> MarketData:
        """
        Return current market data for one symbol.

        Parameters
        ----------
        symbol:
            Stock symbol, for example:
            - FPT
            - HPG
            - MBB
        """

        raise NotImplementedError

    def normalize_symbol(
        self,
        symbol: str,
    ) -> str:
        """
        Normalize and validate stock symbol.

        Provider implementations should call this helper
        before making an external request.
        """

        if symbol is None:
            raise ValueError(
                "symbol must not be empty"
            )

        normalized_symbol = str(
            symbol
        ).strip().upper()

        if not normalized_symbol:
            raise ValueError(
                "symbol must not be empty"
            )

        return normalized_symbol