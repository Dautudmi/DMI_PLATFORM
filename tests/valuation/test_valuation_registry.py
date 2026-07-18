from __future__ import annotations

import pytest

from dmi_core.valuation.base_valuation import (
    BaseValuation,
)
from dmi_core.valuation.ev_ebitda_valuation import (
    EVEBITDAValuation,
)
from dmi_core.valuation.pb_valuation import (
    PBValuation,
)
from dmi_core.valuation.pe_valuation import (
    PEValuation,
)
from dmi_core.valuation.valuation_registry import (
    ValuationRegistry,
)


class FakeValuation(
    BaseValuation
):
    def evaluate(
        self,
        current_price: float | None = None,
    ):
        raise NotImplementedError


class NotAValuation:
    pass


def test_empty_registry() -> None:
    registry = ValuationRegistry()

    assert len(registry) == 0
    assert registry.models() == ()


def test_default_registry_contains_all_models() -> None:
    registry = ValuationRegistry.default()

    assert len(registry) == 3

    assert registry.models() == (
        PEValuation,
        PBValuation,
        EVEBITDAValuation,
    )

    assert registry.contains(
        PEValuation
    ) is True

    assert registry.contains(
        PBValuation
    ) is True

    assert registry.contains(
        EVEBITDAValuation
    ) is True


def test_register_model() -> None:
    registry = ValuationRegistry()

    registry.register(
        FakeValuation
    )

    assert registry.models() == (
        FakeValuation,
    )


def test_registry_preserves_order() -> None:
    registry = ValuationRegistry()

    registry.register(
        PEValuation
    )

    registry.register(
        PBValuation
    )

    registry.register(
        EVEBITDAValuation
    )

    registry.register(
        FakeValuation
    )

    assert registry.models() == (
        PEValuation,
        PBValuation,
        EVEBITDAValuation,
        FakeValuation,
    )


def test_rejects_duplicate_model() -> None:
    registry = ValuationRegistry(
        models=[
            PEValuation,
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "valuation model is already registered"
        ),
    ):
        registry.register(
            PEValuation
        )


def test_rejects_none_model() -> None:
    registry = ValuationRegistry()

    with pytest.raises(
        ValueError,
        match=(
            "valuation model must not be None"
        ),
    ):
        registry.register(
            None
        )


def test_rejects_model_instance() -> None:
    registry = ValuationRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "valuation model must be a class"
        ),
    ):
        registry.register(
            object()
        )


def test_rejects_non_valuation_class() -> None:
    registry = ValuationRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "valuation model must inherit "
            "BaseValuation"
        ),
    ):
        registry.register(
            NotAValuation
        )


def test_unregister_model() -> None:
    registry = ValuationRegistry(
        models=[
            PEValuation,
            PBValuation,
            EVEBITDAValuation,
            FakeValuation,
        ]
    )

    registry.unregister(
        EVEBITDAValuation
    )

    assert registry.models() == (
        PEValuation,
        PBValuation,
        FakeValuation,
    )


def test_unregister_rejects_missing_model() -> None:
    registry = ValuationRegistry()

    with pytest.raises(
        ValueError,
        match=(
            "valuation model is not registered"
        ),
    ):
        registry.unregister(
            PEValuation
        )


def test_clear_registry() -> None:
    registry = ValuationRegistry.default()

    registry.clear()

    assert len(registry) == 0
    assert registry.models() == ()


def test_registry_is_iterable() -> None:
    registry = ValuationRegistry.default()

    assert tuple(
        registry
    ) == (
        PEValuation,
        PBValuation,
        EVEBITDAValuation,
    )