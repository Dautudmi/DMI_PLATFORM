from __future__ import annotations

from collections.abc import Iterable
from typing import TypeAlias

from dmi_core.valuation.base_valuation import BaseValuation
from dmi_core.valuation.ev_ebitda_valuation import (
    EVEBITDAValuation,
)
from dmi_core.valuation.pb_valuation import PBValuation
from dmi_core.valuation.pe_valuation import PEValuation


ValuationModelType: TypeAlias = type


class ValuationRegistry:
    """
    Registry for valuation model classes.

    Supports:
    - V1 models inheriting BaseValuation
    - V2 models implementing evaluate()
    """

    def __init__(
        self,
        models: Iterable[type] | None = None,
    ) -> None:
        self._models: list[type] = []

        if models is not None:
            for model in models:
                self.register(model)

    @classmethod
    def default(
        cls,
    ) -> ValuationRegistry:
        return cls(
            models=[
                PEValuation,
                PBValuation,
                EVEBITDAValuation,
            ]
        )

    def register(
        self,
        model: type,
    ) -> None:
        self._validate_model(model)

        if model in self._models:
            raise ValueError(
                "valuation model is already registered: "
                f"{model.__name__}"
            )

        self._models.append(model)

    def unregister(
        self,
        model: type,
    ) -> None:
        self._validate_model(model)

        if model not in self._models:
            raise ValueError(
                "valuation model is not registered: "
                f"{model.__name__}"
            )

        self._models.remove(model)

    def contains(
        self,
        model: type,
    ) -> bool:
        self._validate_model(model)
        return model in self._models

    def models(
        self,
    ) -> tuple[type, ...]:
        return tuple(self._models)

    def clear(
        self,
    ) -> None:
        self._models.clear()

    def __len__(
        self,
    ) -> int:
        return len(self._models)

    def __iter__(
        self,
    ):
        return iter(self.models())

    def _validate_model(
        self,
        model: type,
    ) -> None:
        if model is None:
            raise ValueError(
                "valuation model must not be None"
            )

        if not isinstance(model, type):
            raise TypeError(
                "valuation model must be a class"
            )

        if issubclass(model, BaseValuation):
            return

        evaluate = getattr(
            model,
            "evaluate",
            None,
        )

        if callable(evaluate):
            return

        raise TypeError(
            "valuation model must inherit BaseValuation "
            "or implement evaluate()"
        )