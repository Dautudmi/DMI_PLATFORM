from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class MarketData:
    """
    Standard market snapshot for one stock.

    FinancialStatement phản ánh tình hình doanh nghiệp.

    MarketData phản ánh trạng thái thị trường.

    Hai model này tách biệt hoàn toàn.
    """

    # Identity
    symbol: str

    # Price
    current_price: Optional[float] = None
    previous_close: Optional[float] = None

    # Shares
    shares_outstanding: Optional[float] = None
    free_float_shares: Optional[float] = None

    # Market value
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None

    # Trading
    volume: Optional[float] = None
    average_volume_20: Optional[float] = None
    average_volume_50: Optional[float] = None

    # Risk
    beta: Optional[float] = None

    # Metadata
    provider: str = "DMI"
    currency: str = "VND"
    schema_version: str = "1.0"

    @property
    def has_price(self) -> bool:
        return (
            self.current_price is not None
            and self.current_price > 0
        )

    @property
    def has_shares(self) -> bool:
        return (
            self.shares_outstanding is not None
            and self.shares_outstanding > 0
        )

    @property
    def has_market_cap(self) -> bool:
        return (
            self.market_cap is not None
            and self.market_cap > 0
        )

    @property
    def has_enterprise_value(self) -> bool:
        return (
            self.enterprise_value is not None
            and self.enterprise_value > 0
        )

    @property
    def succeeded(self) -> bool:
        return self.has_price