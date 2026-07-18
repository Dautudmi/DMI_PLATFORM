from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dmi_core.decision.decision_result import DecisionResult
from dmi_core.models.financial_statement import FinancialStatement


@dataclass(slots=True)
class AnalysisResult:
    """
    Final output of the Daily Analysis Pipeline.

    This object aggregates every major stage of the
    analysis process into a single immutable result.
    """

    symbol: str

    statement: FinancialStatement | None = None

    financial_analysis: Any = None

    valuation_result: Any = None

    weighted_valuation: Any = None

    decision: DecisionResult | None = None

    provider_name: str = ""

    schema_version: str = "1.0"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def succeeded(self) -> bool:
        return (
            self.statement is not None
            and self.decision is not None
        )

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.metadata.get(
            key,
            default,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "provider_name": self.provider_name,
            "schema_version": self.schema_version,
            "succeeded": self.succeeded,
            "metadata": dict(self.metadata),
        }