from __future__ import annotations

import pytest

from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.models.free_cash_flow import (
    FreeCashFlow,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
)
from dmi_core.valuation.dcf_projection import (
    DCFProjection,
)
from dmi_core.valuation.dcf_valuation import (
    DCFValuation,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)


def create_statement(
    free_cash_flow: float | None = 100.0,
    operating_cash_flow: float | None = None,
    capex: float | None = None,
    total_debt: float | None = 200.0,
    cash: float | None = 50.0,
    charter_capital: float | None = 1_000.0,
    include_cash_flow: bool = True,
) -> FinancialStatement:
    """
    Create a FinancialStatement for DCF tests.

    Default DCF assumptions:

        Base FCF = 100
        Growth rate = 10%
        Discount rate = 12%
        Terminal growth rate = 3%
        Projection period = 5 years

    Expected enterprise value:

        approximately 1,519.690254

    Default equity value:

        1,519.690254 - 200 + 50
        = 1,369.690254

    Default intrinsic value per share:

        1,369.690254 / 1,000 × 10,000
        = approximately 13,696.902538
    """

    balance_sheet = BalanceSheet(
        symbol="AAA",
        year=2025,
        quarter=4,
        total_debt=total_debt,
        cash=cash,
        charter_capital=charter_capital,
        equity=2_000.0,
    )

    income_statement = IncomeStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
        net_profit=200.0,
        eps=2_000.0,
    )

    cash_flow = None

    if include_cash_flow:
        cash_flow = FreeCashFlow(
            symbol="AAA",
            year=2025,
            quarter=4,
            operating_cash_flow=operating_cash_flow,
            capex=capex,
            free_cash_flow=free_cash_flow,
        )

    return FinancialStatement(
        symbol="AAA",
        year=2025,
        quarter=4,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
        free_cash_flow=cash_flow,
    )


def test_dcf_calculates_intrinsic_value() -> None:
    statement = create_statement()

    valuation = DCFValuation(
        statement=statement,
    )

    result = valuation.evaluate()

    assert result.method == "DCF"

    assert result.intrinsic_value == pytest.approx(
        13_696.902537986925
    )

    assert result.current_price is None
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_dcf_returns_buy() -> None:
    result = DCFValuation(
        statement=create_statement(),
    ).evaluate(
        current_price=9_000.0,
    )

    intrinsic_value = 13_696.902537986925

    assert result.intrinsic_value == pytest.approx(
        intrinsic_value
    )

    assert result.current_price == pytest.approx(
        9_000.0
    )

    assert result.upside == pytest.approx(
        (intrinsic_value - 9_000.0)
        / 9_000.0
    )

    assert result.downside == pytest.approx(
        0.0
    )

    assert result.margin_of_safety == pytest.approx(
        (intrinsic_value - 9_000.0)
        / intrinsic_value
    )

    assert result.recommendation == "BUY"


def test_dcf_returns_watch() -> None:
    result = DCFValuation(
        statement=create_statement(),
    ).evaluate(
        current_price=12_500.0,
    )

    intrinsic_value = 13_696.902537986925

    assert result.upside == pytest.approx(
        (intrinsic_value - 12_500.0)
        / 12_500.0
    )

    assert result.downside == pytest.approx(
        0.0
    )

    assert result.margin_of_safety == pytest.approx(
        (intrinsic_value - 12_500.0)
        / intrinsic_value
    )

    assert result.recommendation == "WATCH"


def test_dcf_returns_avoid() -> None:
    result = DCFValuation(
        statement=create_statement(),
    ).evaluate(
        current_price=15_000.0,
    )

    intrinsic_value = 13_696.902537986925

    assert result.upside == pytest.approx(
        (intrinsic_value - 15_000.0)
        / 15_000.0
    )

    assert result.downside == pytest.approx(
        (15_000.0 - intrinsic_value)
        / 15_000.0
    )

    assert result.margin_of_safety == pytest.approx(
        (intrinsic_value - 15_000.0)
        / intrinsic_value
    )

    assert result.recommendation == "AVOID"


def test_dcf_without_free_cash_flow_model_returns_na() -> None:
    statement = create_statement(
        include_cash_flow=False,
    )

    result = DCFValuation(
        statement=statement,
    ).evaluate(
        current_price=10_000.0,
    )

    assert result.method == "DCF"
    assert result.intrinsic_value is None
    assert result.current_price == pytest.approx(
        10_000.0
    )
    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_dcf_without_resolved_cash_flow_returns_na() -> None:
    statement = create_statement(
        free_cash_flow=None,
        operating_cash_flow=None,
        capex=None,
    )

    result = DCFValuation(
        statement=statement,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_calculates_cash_flow_from_ocf_and_capex() -> None:
    statement = create_statement(
        free_cash_flow=None,
        operating_cash_flow=150.0,
        capex=50.0,
    )

    result = DCFValuation(
        statement=statement,
    ).evaluate()

    # Resolved FCF = 150 - 50 = 100.
    assert result.intrinsic_value == pytest.approx(
        13_696.902537986925
    )


def test_dcf_prefers_explicit_free_cash_flow() -> None:
    statement = create_statement(
        free_cash_flow=100.0,
        operating_cash_flow=300.0,
        capex=50.0,
    )

    result = DCFValuation(
        statement=statement,
    ).evaluate()

    # Explicit FCF 100 is used instead of calculated FCF 250.
    assert result.intrinsic_value == pytest.approx(
        13_696.902537986925
    )


def test_dcf_without_charter_capital_returns_na() -> None:
    result = DCFValuation(
        statement=create_statement(
            charter_capital=None,
        ),
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_with_zero_charter_capital_returns_na() -> None:
    result = DCFValuation(
        statement=create_statement(
            charter_capital=0.0,
        ),
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_with_negative_charter_capital_returns_na() -> None:
    result = DCFValuation(
        statement=create_statement(
            charter_capital=-1_000.0,
        ),
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_treats_missing_debt_as_zero() -> None:
    result = DCFValuation(
        statement=create_statement(
            total_debt=None,
            cash=50.0,
        ),
    ).evaluate()

    # Equity value:
    # 1,519.690254 - 0 + 50
    # = 1,569.690254
    #
    # Intrinsic value:
    # 1,569.690254 / 1,000 × 10,000
    assert result.intrinsic_value == pytest.approx(
        15_696.902537986925
    )


def test_dcf_treats_missing_cash_as_zero() -> None:
    result = DCFValuation(
        statement=create_statement(
            total_debt=200.0,
            cash=None,
        ),
    ).evaluate()

    # Equity value:
    # 1,519.690254 - 200
    # = 1,319.690254
    assert result.intrinsic_value == pytest.approx(
        13_196.902537986925
    )


def test_dcf_with_non_positive_equity_value_returns_na() -> None:
    result = DCFValuation(
        statement=create_statement(
            total_debt=2_000.0,
            cash=0.0,
        ),
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_rejects_discount_rate_not_above_terminal_growth() -> None:
    config = ValuationConfig(
        discount_rate=0.03,
        terminal_growth_rate=0.03,
    )

    result = DCFValuation(
        statement=create_statement(),
        config=config,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_rejects_discount_rate_below_terminal_growth() -> None:
    config = ValuationConfig(
        discount_rate=0.02,
        terminal_growth_rate=0.03,
    )

    result = DCFValuation(
        statement=create_statement(),
        config=config,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_rejects_non_positive_discount_rate() -> None:
    config = ValuationConfig(
        discount_rate=0.0,
        terminal_growth_rate=0.03,
    )

    result = DCFValuation(
        statement=create_statement(),
        config=config,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_rejects_invalid_terminal_growth_rate() -> None:
    config = ValuationConfig(
        discount_rate=0.12,
        terminal_growth_rate=-1.0,
    )

    result = DCFValuation(
        statement=create_statement(),
        config=config,
    ).evaluate()

    assert result.intrinsic_value is None
    assert result.recommendation == "N/A"


def test_dcf_without_valid_current_price() -> None:
    result = DCFValuation(
        statement=create_statement(),
    ).evaluate(
        current_price=0.0,
    )

    assert result.intrinsic_value == pytest.approx(
        13_696.902537986925
    )

    assert result.current_price == pytest.approx(
        0.0
    )

    assert result.upside is None
    assert result.downside is None
    assert result.margin_of_safety is None
    assert result.recommendation == "N/A"


def test_dcf_uses_custom_growth_rate() -> None:
    default_result = DCFValuation(
        statement=create_statement(),
        growth_rate=0.10,
    ).evaluate()

    higher_growth_result = DCFValuation(
        statement=create_statement(),
        growth_rate=0.15,
    ).evaluate()

    assert default_result.intrinsic_value is not None
    assert higher_growth_result.intrinsic_value is not None

    assert (
        higher_growth_result.intrinsic_value
        > default_result.intrinsic_value
    )


def test_dcf_uses_custom_projection_years() -> None:
    five_year_result = DCFValuation(
        statement=create_statement(),
        projection_years=5,
    ).evaluate()

    ten_year_result = DCFValuation(
        statement=create_statement(),
        projection_years=10,
    ).evaluate()

    assert five_year_result.intrinsic_value is not None
    assert ten_year_result.intrinsic_value is not None

    assert (
        ten_year_result.intrinsic_value
        > five_year_result.intrinsic_value
    )


@pytest.mark.parametrize(
    "growth_rate",
    [
        "0.10",
        True,
        object(),
    ],
)
def test_dcf_rejects_non_numeric_growth_rate(
    growth_rate,
) -> None:
    with pytest.raises(
        TypeError,
        match="growth_rate must be numeric",
    ):
        DCFValuation(
            statement=create_statement(),
            growth_rate=growth_rate,
        )


@pytest.mark.parametrize(
    "growth_rate",
    [
        -1.0,
        -2.0,
    ],
)
def test_dcf_rejects_growth_rate_at_or_below_minus_one(
    growth_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "growth_rate must be greater than -1"
        ),
    ):
        DCFValuation(
            statement=create_statement(),
            growth_rate=growth_rate,
        )


@pytest.mark.parametrize(
    "projection_years",
    [
        5.0,
        "5",
        True,
        object(),
    ],
)
def test_dcf_rejects_non_integer_projection_years(
    projection_years,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "projection_years must be an integer"
        ),
    ):
        DCFValuation(
            statement=create_statement(),
            projection_years=projection_years,
        )


@pytest.mark.parametrize(
    "projection_years",
    [
        0,
        -1,
    ],
)
def test_dcf_rejects_non_positive_projection_years(
    projection_years: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "projection_years must be "
            "greater than zero"
        ),
    ):
        DCFValuation(
            statement=create_statement(),
            projection_years=projection_years,
        )


def test_dcf_preserves_custom_metadata() -> None:
    config = ValuationConfig(
        source="DMI-DCF",
        schema_version="3.2",
    )

    result = DCFValuation(
        statement=create_statement(),
        config=config,
    ).evaluate()

    assert result.source == "DMI-DCF"
    assert result.schema_version == "3.2"


def test_dcf_description_is_available() -> None:
    result = DCFValuation(
        statement=create_statement(),
    ).evaluate()

    assert result.description is not None
    assert "DCF" in result.description


def test_dcf_uses_injected_projection() -> None:
    projection = DCFProjection()

    valuation = DCFValuation(
        statement=create_statement(),
        projection=projection,
    )

    assert valuation.projection is projection