from __future__ import annotations

from dataclasses import dataclass, field

from dmi_core.valuation.valuation_result import (
    ValuationResult,
)


@dataclass(slots=True)
class WeightedFairValueResult:
    """
    Kết quả tổng hợp nhiều phương pháp định giá.

    WeightedFairValueResult giữ các thuộc tính quan trọng
    tương thích về mặt dữ liệu với ValuationResult:

    - method
    - intrinsic_value
    - current_price
    - upside
    - downside
    - margin_of_safety
    - recommendation
    - description
    - source
    - schema_version

    Ngoài ra còn lưu:
    - components: các kết quả valuation đầu vào
    - normalized_weights: trọng số thực tế sau khi chuẩn hóa
    """

    method: str

    intrinsic_value: float | None

    current_price: float | None

    upside: float | None

    downside: float | None

    margin_of_safety: float | None

    recommendation: str

    components: tuple[
        ValuationResult,
        ...,
    ] = field(
        default_factory=tuple
    )

    normalized_weights: dict[
        str,
        float,
    ] = field(
        default_factory=dict
    )

    description: str | None = None

    source: str = "DMI"

    schema_version: str = "3.0"

    @property
    def fair_value(
        self,
    ) -> float | None:
        """
        Alias rõ nghĩa của intrinsic_value.
        """

        return self.intrinsic_value

    @property
    def valid_component_count(
        self,
    ) -> int:
        """
        Số valuation component thực sự được dùng
        để tính Weighted Fair Value.
        """

        return len(
            self.normalized_weights
        )

    def get_weight(
        self,
        method: str,
    ) -> float:
        """
        Lấy trọng số đã chuẩn hóa của một phương pháp.

        Ví dụ:
            result.get_weight("PE")
            result.get_weight("PB")
        """

        normalized_method = (
            str(method).strip().upper()
        )

        return self.normalized_weights.get(
            normalized_method,
            0.0,
        )