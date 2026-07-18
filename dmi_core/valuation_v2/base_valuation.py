from __future__ import annotations

from abc import ABC, abstractmethod

from dmi_core.market.market_data import MarketData
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)
from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


class BaseValuationV2(ABC):
    """
    Base contract for DMI Valuation V2.

    V1 contract:

        model = Valuation(statement)
        result = model.evaluate(current_price)

    V2 contract:

        model = ValuationV2(config)
        result = model.evaluate(
            statement=statement,
            market=market,
        )

    V2 sử dụng đồng thời:

        FinancialStatement
                +
            MarketData

    Nhờ đó valuation model không còn phụ thuộc vào việc
    báo cáo tài chính phải chứa sẵn:

    - EPS
    - BVPS
    - số lượng cổ phiếu lưu hành
    - market capitalization
    - enterprise value
    """

    method: str = "UNKNOWN"

    def __init__(
        self,
        config: ValuationConfig | None = None,
    ) -> None:
        if config is None:
            config = ValuationConfig()

        self._config = config

    @property
    def config(
        self,
    ) -> ValuationConfig:
        return self._config

    @abstractmethod
    def evaluate(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> ValuationResult:
        """
        Calculate intrinsic value for one stock.

        Implementations must return ValuationResult
        instead of returning a raw number.
        """

        raise NotImplementedError

    def validate_inputs(
        self,
        statement: FinancialStatement,
        market: MarketData,
    ) -> None:
        """
        Validate shared inputs before valuation.
        """

        if statement is None:
            raise ValueError(
                "statement must not be None"
            )

        if market is None:
            raise ValueError(
                "market must not be None"
            )

        if not hasattr(
            statement,
            "symbol",
        ):
            raise TypeError(
                "statement must have symbol"
            )

        if not hasattr(
            statement,
            "balance_sheet",
        ):
            raise TypeError(
                "statement must have balance_sheet"
            )

        if not hasattr(
            statement,
            "income_statement",
        ):
            raise TypeError(
                "statement must have income_statement"
            )

        if not hasattr(
            market,
            "symbol",
        ):
            raise TypeError(
                "market must have symbol"
            )

        if not hasattr(
            market,
            "current_price",
        ):
            raise TypeError(
                "market must have current_price"
            )

        statement_symbol = self.normalize_symbol(
            statement.symbol
        )

        market_symbol = self.normalize_symbol(
            market.symbol
        )

        if statement_symbol != market_symbol:
            raise ValueError(
                "statement symbol and market symbol "
                "must be identical"
            )

    def create_result(
        self,
        intrinsic_value: float | None,
        current_price: float | None,
        description: str | None = None,
    ) -> ValuationResult:
        """
        Build a ValuationResult using the existing
        DMI ValuationResult contract.
        """

        normalized_intrinsic_value = (
            self.positive_or_none(
                intrinsic_value
            )
        )

        normalized_current_price = (
            self.positive_or_none(
                current_price
            )
        )

        upside = self.calculate_upside(
            intrinsic_value=normalized_intrinsic_value,
            current_price=normalized_current_price,
        )

        downside = self.calculate_downside(
            upside=upside,
        )

        margin_of_safety = (
            self.calculate_margin_of_safety(
                intrinsic_value=(
                    normalized_intrinsic_value
                ),
                current_price=(
                    normalized_current_price
                ),
            )
        )

        recommendation = self.create_recommendation(
            margin_of_safety=margin_of_safety,
        )

        return ValuationResult(
            method=self.method,
            intrinsic_value=(
                normalized_intrinsic_value
            ),
            current_price=(
                normalized_current_price
            ),
            upside=upside,
            downside=downside,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation,
            description=description,
            source=self._config.source,
            schema_version=(
                self._config.schema_version
            ),
        )

    def create_unavailable_result(
        self,
        current_price: float | None,
        description: str,
    ) -> ValuationResult:
        """
        Return a standard result when valuation cannot
        be calculated because required data is missing.
        """

        return ValuationResult(
            method=self.method,
            intrinsic_value=None,
            current_price=(
                self.positive_or_none(
                    current_price
                )
            ),
            upside=None,
            downside=None,
            margin_of_safety=None,
            recommendation="N/A",
            description=description,
            source=self._config.source,
            schema_version=(
                self._config.schema_version
            ),
        )

    def create_recommendation(
        self,
        margin_of_safety: float | None,
    ) -> str:
        """
        Convert margin of safety into a valuation signal.

        BUY:
            margin of safety meets or exceeds
            required_margin_of_safety.

        HOLD:
            intrinsic value remains above current price,
            but the required safety margin is not met.

        SELL:
            intrinsic value is below current price.

        N/A:
            valuation cannot be calculated.
        """

        if margin_of_safety is None:
            return "N/A"

        if (
            margin_of_safety
            >= self._config.required_margin_of_safety
        ):
            return "BUY"

        if margin_of_safety > 0:
            return "HOLD"

        return "SELL"

    @staticmethod
    def calculate_upside(
        intrinsic_value: float | None,
        current_price: float | None,
    ) -> float | None:
        """
        Upside expressed as a decimal ratio.

        Example:
            intrinsic value = 120
            current price = 100
            upside = 0.20
        """

        if (
            intrinsic_value is None
            or current_price is None
            or current_price <= 0
        ):
            return None

        return (
            intrinsic_value
            / current_price
            - 1.0
        )

    @staticmethod
    def calculate_downside(
        upside: float | None,
    ) -> float | None:
        """
        Downside is only reported when upside is negative.
        """

        if upside is None:
            return None

        if upside >= 0:
            return 0.0

        return abs(
            upside
        )

    @staticmethod
    def calculate_margin_of_safety(
        intrinsic_value: float | None,
        current_price: float | None,
    ) -> float | None:
        """
        Margin of safety:

            (Intrinsic Value - Current Price)
            / Intrinsic Value
        """

        if (
            intrinsic_value is None
            or intrinsic_value <= 0
            or current_price is None
            or current_price <= 0
        ):
            return None

        return (
            intrinsic_value
            - current_price
        ) / intrinsic_value

    @staticmethod
    def normalize_symbol(
        symbol: object,
    ) -> str:
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

    @staticmethod
    def positive_or_none(
        value: object,
    ) -> float | None:
        """
        Normalize a positive numeric value.
        """

        if value is None:
            return None

        try:
            normalized_value = float(
                value
            )
        except (TypeError, ValueError):
            return None

        if normalized_value <= 0:
            return None

        return normalized_value

    @staticmethod
    def non_negative_or_zero(
        value: object,
    ) -> float:
        """
        Normalize a non-negative numeric value.
        """

        if value is None:
            return 0.0

        try:
            normalized_value = float(
                value
            )
        except (TypeError, ValueError):
            return 0.0

        if normalized_value < 0:
            return 0.0

        return normalized_value