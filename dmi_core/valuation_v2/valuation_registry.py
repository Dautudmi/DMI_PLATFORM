from __future__ import annotations

from collections.abc import Iterable
from typing import TypeAlias

from dmi_core.valuation_v2.base_valuation import (
    BaseValuationV2,
)
from dmi_core.valuation_v2.ev_ebitda_valuation import (
    EVEBITDAValuationV2,
)
from dmi_core.valuation_v2.pb_valuation import (
    PBValuationV2,
)
from dmi_core.valuation_v2.pe_valuation import (
    PEValuationV2,
)


ValuationModelV2Type: TypeAlias = type[
    BaseValuationV2
]


class ValuationRegistryV2:
    """
    Registry dành riêng cho Valuation V2.

    Responsibility:

    - đăng ký valuation model V2
    - ngăn đăng ký trùng
    - duy trì thứ tự thực thi
    - cung cấp registry mặc định
    - không ảnh hưởng ValuationRegistry của V1

    Registry mặc định:

    1. PEValuationV2
    2. PBValuationV2
    3. EVEBITDAValuationV2
    """

    def __init__(
        self,
        models: Iterable[
            ValuationModelV2Type
        ] | None = None,
    ) -> None:
        self._models: list[
            ValuationModelV2Type
        ] = []

        if models is not None:
            for model in models:
                self.register(
                    model
                )

    @classmethod
    def default(
        cls,
    ) -> ValuationRegistryV2:
        """
        Tạo registry mặc định của Valuation V2.
        """

        return cls(
            models=[
                PEValuationV2,
                PBValuationV2,
                EVEBITDAValuationV2,
            ]
        )

    def register(
        self,
        model: ValuationModelV2Type,
    ) -> None:
        """
        Đăng ký một valuation model V2.

        Model phải:

        - là class
        - kế thừa BaseValuationV2
        - chưa tồn tại trong registry
        """

        self._validate_model(
            model
        )

        if model in self._models:
            raise ValueError(
                "valuation V2 model is already "
                "registered: "
                f"{model.__name__}"
            )

        self._models.append(
            model
        )

    def unregister(
        self,
        model: ValuationModelV2Type,
    ) -> None:
        """
        Gỡ một model khỏi registry.
        """

        self._validate_model(
            model
        )

        if model not in self._models:
            raise ValueError(
                "valuation V2 model is not "
                "registered: "
                f"{model.__name__}"
            )

        self._models.remove(
            model
        )

    def contains(
        self,
        model: ValuationModelV2Type,
    ) -> bool:
        """
        Kiểm tra model đã được đăng ký hay chưa.
        """

        self._validate_model(
            model
        )

        return model in self._models

    def models(
        self,
    ) -> tuple[
        ValuationModelV2Type,
        ...,
    ]:
        """
        Trả về immutable snapshot của registry.
        """

        return tuple(
            self._models
        )

    def model_names(
        self,
    ) -> tuple[
        str,
        ...,
    ]:
        """
        Trả về tên các model theo thứ tự thực thi.
        """

        return tuple(
            model.__name__
            for model in self._models
        )

    def clear(
        self,
    ) -> None:
        """
        Xóa toàn bộ model khỏi registry.
        """

        self._models.clear()

    def __len__(
        self,
    ) -> int:
        return len(
            self._models
        )

    def __iter__(
        self,
    ):
        return iter(
            self.models()
        )

    def _validate_model(
        self,
        model: ValuationModelV2Type,
    ) -> None:
        """
        Validate model trước khi thao tác registry.
        """

        if model is None:
            raise ValueError(
                "valuation V2 model must not be None"
            )

        if not isinstance(
            model,
            type,
        ):
            raise TypeError(
                "valuation V2 model must be a class"
            )

        if not issubclass(
            model,
            BaseValuationV2,
        ):
            raise TypeError(
                "valuation V2 model must inherit "
                "BaseValuationV2"
            )