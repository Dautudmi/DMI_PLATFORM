from __future__ import annotations

from dataclasses import dataclass, field

from dmi_core.market.market_data import (
    MarketData,
)


@dataclass(slots=True)
class MarketResult:
    """
    Result returned by a market-data provider.

    MarketResult giúp application layer xử lý thống nhất:

    - MarketData
    - warnings
    - errors
    - provider metadata

    Ordinary provider failures should normally be represented
    inside errors instead of forcing callers to inspect many
    exception types.
    """

    data: MarketData | None = None

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    errors: tuple[str, ...] = field(
        default_factory=tuple
    )

    provider_name: str = "UNKNOWN"

    symbol: str | None = None

    source: str = "DMI"

    schema_version: str = "1.0"

    @property
    def succeeded(
        self,
    ) -> bool:
        return (
            self.data is not None
            and not self.errors
        )

    @property
    def has_warning(
        self,
    ) -> bool:
        return bool(
            self.warnings
        )

    @property
    def has_error(
        self,
    ) -> bool:
        return bool(
            self.errors
        )

    @property
    def normalized_symbol(
        self,
    ) -> str | None:
        if self.symbol is None:
            return None

        normalized = str(
            self.symbol
        ).strip().upper()

        return normalized or None

    def explain(
        self,
    ) -> str:
        lines = [
            "Market Data Provider",
            f"Provider: {self.provider_name}",
            (
                "Symbol: "
                f"{self.normalized_symbol or 'N/A'}"
            ),
            f"Source: {self.source}",
            f"Success: {self.succeeded}",
        ]

        if self.data is not None:
            lines.extend(
                [
                    "",
                    "Market Data:",
                    (
                        "Current Price: "
                        f"{self.data.current_price}"
                    ),
                    (
                        "Shares Outstanding: "
                        f"{self.data.shares_outstanding}"
                    ),
                    (
                        "Market Cap: "
                        f"{self.data.market_cap}"
                    ),
                ]
            )

        if self.warnings:
            lines.extend(
                [
                    "",
                    "Warnings:",
                ]
            )

            for warning in self.warnings:
                lines.append(
                    f"- {warning}"
                )

        if self.errors:
            lines.extend(
                [
                    "",
                    "Errors:",
                ]
            )

            for error in self.errors:
                lines.append(
                    f"- {error}"
                )

        return "\n".join(
            lines
        )