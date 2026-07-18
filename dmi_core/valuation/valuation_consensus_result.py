from __future__ import annotations

from dataclasses import dataclass, field

from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


@dataclass(slots=True)
class ValuationConsensusResult:
    """
    Aggregate result describing agreement between
    multiple valuation methods.

    The result stores:

    - consensus fair value
    - median fair value
    - minimum and maximum fair value
    - valuation dispersion
    - confidence score
    - valid valuation components
    - detected outlier methods
    """

    method: str

    consensus_value: float | None

    median_value: float | None

    minimum_value: float | None

    maximum_value: float | None

    dispersion: float | None

    confidence: int

    components: tuple[
        ValuationResult,
        ...,
    ] = field(
        default_factory=tuple
    )

    included_methods: tuple[
        str,
        ...,
    ] = field(
        default_factory=tuple
    )

    outlier_methods: tuple[
        str,
        ...,
    ] = field(
        default_factory=tuple
    )

    description: str | None = None

    source: str = "DMI"

    schema_version: str = "1.0"

    @property
    def intrinsic_value(
        self,
    ) -> float | None:
        """
        Compatibility alias for consensus fair value.
        """

        return self.consensus_value

    @property
    def fair_value(
        self,
    ) -> float | None:
        """
        Readable alias for consensus fair value.
        """

        return self.consensus_value

    @property
    def valid_component_count(
        self,
    ) -> int:
        """
        Number of methods included in the consensus.
        """

        return len(
            self.included_methods
        )

    @property
    def outlier_count(
        self,
    ) -> int:
        """
        Number of valuation methods detected as outliers.
        """

        return len(
            self.outlier_methods
        )

    @property
    def is_valid(
        self,
    ) -> bool:
        """
        Whether a consensus value is available.
        """

        return self.consensus_value is not None

    @property
    def has_outliers(
        self,
    ) -> bool:
        return bool(
            self.outlier_methods
        )

    @property
    def agreement_level(
        self,
    ) -> str:
        """
        Human-readable valuation agreement level.

        Dispersion is represented as a ratio:

            0.10 = 10%
        """

        if self.dispersion is None:
            return "N/A"

        if self.dispersion <= 0.10:
            return "HIGH"

        if self.dispersion <= 0.20:
            return "MEDIUM"

        return "LOW"

    def includes_method(
        self,
        method: str,
    ) -> bool:
        normalized_method = (
            str(method).strip().upper()
        )

        return normalized_method in {
            item.upper()
            for item in self.included_methods
        }

    def is_outlier(
        self,
        method: str,
    ) -> bool:
        normalized_method = (
            str(method).strip().upper()
        )

        return normalized_method in {
            item.upper()
            for item in self.outlier_methods
        }

    def explain(
        self,
    ) -> str:
        """
        Return a human-readable consensus explanation.
        """

        if not self.is_valid:
            return (
                "Valuation consensus is unavailable."
            )

        included = (
            ", ".join(self.included_methods)
            if self.included_methods
            else "N/A"
        )

        outliers = (
            ", ".join(self.outlier_methods)
            if self.outlier_methods
            else "None"
        )

        dispersion = (
            f"{self.dispersion * 100:.2f}%"
            if self.dispersion is not None
            else "N/A"
        )

        return "\n".join(
            [
                "Valuation Consensus",
                (
                    "Consensus Value: "
                    f"{self.consensus_value:,.2f}"
                ),
                (
                    "Median Value: "
                    f"{self.median_value:,.2f}"
                ),
                (
                    "Range: "
                    f"{self.minimum_value:,.2f}"
                    " - "
                    f"{self.maximum_value:,.2f}"
                ),
                (
                    "Dispersion: "
                    f"{dispersion}"
                ),
                (
                    "Agreement: "
                    f"{self.agreement_level}"
                ),
                (
                    "Confidence: "
                    f"{self.confidence}%"
                ),
                (
                    "Included Methods: "
                    f"{included}"
                ),
                (
                    "Outlier Methods: "
                    f"{outliers}"
                ),
            ]
        )