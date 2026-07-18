from __future__ import annotations

import pytest

from apps.analysis import (
    AnalysisPipeline,
    AnalysisResult,
    analyze_and_explain,
    analyze_symbol,
)
from dmi_core.decision.decision_engine import (
    DecisionEngine,
)
from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.models.balance_sheet import (
    BalanceSheet,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.models.income_statement import (
    IncomeStatement,
)
from dmi_core.providers.base_provider import (
    BaseProvider,
)
from dmi_core.providers.financial_statement_provider import (
    FinancialStatementProvider,
)
from dmi_core.providers.provider_result import (
    ProviderResult,
)
from dmi_core.valuation.valuation_config import (
    ValuationConfig,
)
from dmi_core.valuation.valuation_engine import (
    ValuationEngine,
)


class FakeProvider(
    BaseProvider
):
    """
    Provider giả dùng riêng cho test.

    Pipeline test không gọi Internet hoặc CafeF API.
    """

    def get_balance_sheet(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ):
        return {}

    def get_income_statement(
        self,
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
    ):
        return {}


def create_statement(
    symbol: str = "AAA",
    net_profit: float | None = 400.0,
    equity: float | None = 2_000.0,
    total_debt: float | None = 1_000.0,
    charter_capital: float | None = 1_000.0,
    eps: float | None = 4_000.0,
) -> FinancialStatement:
    """
    FinancialStatement đủ dữ liệu để:

    - tính ROE
    - tính Debt/Equity
    - định giá PE
    - định giá PB
    """

    balance_sheet = BalanceSheet(
        symbol=symbol,
        year=2025,
        quarter=4,
        total_assets=4_000.0,
        total_debt=total_debt,
        total_liabilities=2_000.0,
        equity=equity,
        charter_capital=charter_capital,
    )

    income_statement = IncomeStatement(
        symbol=symbol,
        year=2025,
        quarter=4,
        revenue=5_000.0,
        gross_profit=1_500.0,
        operating_profit=700.0,
        pre_tax_profit=500.0,
        net_profit=net_profit,
        eps=eps,
    )

    return FinancialStatement(
        symbol=symbol,
        year=2025,
        quarter=4,
        balance_sheet=balance_sheet,
        income_statement=income_statement,
        report_type="NAM",
        provider="TEST",
    )


def create_statement_provider(
) -> FinancialStatementProvider:
    return FinancialStatementProvider(
        provider=FakeProvider(),
        provider_name="FakeProvider",
        source="TEST",
        schema_version="1.0",
    )


def create_pipeline(
) -> AnalysisPipeline:
    valuation_engine = ValuationEngine(
        config=ValuationConfig(
            target_pe=10.0,
            target_pb=1.5,
            required_margin_of_safety=0.25,
        )
    )

    return AnalysisPipeline(
        statement_provider=(
            create_statement_provider()
        ),
        valuation_engine=valuation_engine,
        decision_engine=DecisionEngine(),
        default_policy=DecisionPolicy(),
    )


def create_success_provider_result(
    symbol: str = "AAA",
) -> ProviderResult:
    return ProviderResult(
        statement=create_statement(
            symbol=symbol
        ),
        warnings=(
            "Test warning",
        ),
        errors=(),
        provider_name="FakeProvider",
        symbol=symbol,
        period="NAM",
        page_size=4,
        source="TEST",
        schema_version="1.0",
    )


def test_pipeline_initialization_exposes_dependencies(
) -> None:
    statement_provider = (
        create_statement_provider()
    )

    valuation_engine = ValuationEngine()

    decision_engine = DecisionEngine()

    policy = DecisionPolicy()

    pipeline = AnalysisPipeline(
        statement_provider=statement_provider,
        valuation_engine=valuation_engine,
        decision_engine=decision_engine,
        default_policy=policy,
    )

    assert (
        pipeline.statement_provider
        is statement_provider
    )

    assert (
        pipeline.valuation_engine
        is valuation_engine
    )

    assert (
        pipeline.decision_engine
        is decision_engine
    )

    assert pipeline.default_policy is policy


def test_pipeline_rejects_none_provider(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "statement_provider must not be None"
        ),
    ):
        AnalysisPipeline(
            statement_provider=None
        )


def test_pipeline_rejects_invalid_provider_type(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "statement_provider must be a "
            "FinancialStatementProvider"
        ),
    ):
        AnalysisPipeline(
            statement_provider=object()
        )


def test_pipeline_runs_successfully(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    provider_result = (
        create_success_provider_result(
            symbol="AAA"
        )
    )

    def fake_get(
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
        raise_on_error: bool = False,
    ) -> ProviderResult:
        assert symbol == "AAA"
        assert period == "NAM"
        assert page_size == 4
        assert raise_on_error is False

        return provider_result

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        fake_get,
    )

    result = pipeline.run(
        symbol=" aaa ",
        current_price=20_000.0,
    )

    assert isinstance(
        result,
        AnalysisResult,
    )

    assert result.symbol == "AAA"
    assert result.statement is not None

    assert (
        result.financial_analysis
        is not None
    )

    assert result.valuation_result is not None

    methods = {
    valuation.method
    for valuation in result.valuation_result
    }

    assert "PE" in methods
    assert "PB" in methods

    assert len(result.valuation_result) >= 2

    assert (
        result.weighted_valuation
        is not None
    )

    assert (
        result.weighted_valuation.method
        == "WEIGHTED"
    )

    assert result.decision is not None
    assert result.succeeded is True

    assert (
        result.get_metadata(
            "provider_succeeded"
        )
        is True
    )

    assert result.get_metadata(
        "provider_warnings"
    ) == (
        "Test warning",
    )

    assert result.get_metadata(
        "valuation_count"
    ) == len(
        result.valuation_result
    )

    assert result.get_metadata(
        "pipeline_succeeded"
    ) is True


def test_pipeline_returns_failed_result_when_provider_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    provider_result = ProviderResult(
        statement=None,
        warnings=(),
        errors=(
            "Provider unavailable",
        ),
        provider_name="FakeProvider",
        symbol="AAA",
        period="NAM",
        page_size=4,
        source="TEST",
        schema_version="1.0",
    )

    def fake_get(
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
        raise_on_error: bool = False,
    ) -> ProviderResult:
        return provider_result

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        fake_get,
    )

    result = pipeline.run(
        symbol="AAA",
        current_price=20_000.0,
    )

    assert isinstance(
        result,
        AnalysisResult,
    )

    assert result.succeeded is False
    assert result.statement is None

    assert (
        result.financial_analysis
        is None
    )

    assert result.decision is None

    assert (
        result.get_metadata(
            "provider_succeeded"
        )
        is False
    )

    assert result.get_metadata(
        "provider_errors"
    ) == (
        "Provider unavailable",
    )

    assert (
        result.get_metadata(
            "pipeline_error"
        )
        == (
            "Financial statement provider "
            "did not produce a valid statement."
        )
    )


def test_pipeline_can_raise_when_provider_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    provider_result = ProviderResult(
        statement=None,
        errors=(
            "Provider unavailable",
        ),
        provider_name="FakeProvider",
        symbol="AAA",
        period="NAM",
        page_size=4,
    )

    def fake_get(
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
        raise_on_error: bool = False,
    ) -> ProviderResult:
        return provider_result

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        fake_get,
    )

    with pytest.raises(
        RuntimeError,
        match="Financial Statement Provider",
    ):
        pipeline.run(
            symbol="AAA",
            current_price=20_000.0,
            raise_on_error=True,
        )


def test_pipeline_captures_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    def broken_get(
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
        raise_on_error: bool = False,
    ) -> ProviderResult:
        raise RuntimeError(
            "Unexpected provider error"
        )

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        broken_get,
    )

    result = pipeline.run(
        symbol="AAA",
        current_price=20_000.0,
        raise_on_error=False,
    )

    assert result.succeeded is False

    assert result.get_metadata(
        "pipeline_succeeded"
    ) is False

    assert result.get_metadata(
        "pipeline_error_type"
    ) == "RuntimeError"

    assert result.get_metadata(
        "pipeline_error"
    ) == "Unexpected provider error"


def test_pipeline_propagates_unexpected_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    def broken_get(
        symbol: str,
        period: str = "NAM",
        page_size: int = 4,
        raise_on_error: bool = False,
    ) -> ProviderResult:
        raise RuntimeError(
            "Unexpected provider error"
        )

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        broken_get,
    )

    with pytest.raises(
        RuntimeError,
        match="Unexpected provider error",
    ):
        pipeline.run(
            symbol="AAA",
            current_price=20_000.0,
            raise_on_error=True,
        )


@pytest.mark.parametrize(
    (
        "symbol",
        "expected_exception",
        "expected_message",
    ),
    [
        (
            None,
            ValueError,
            "symbol must not be empty",
        ),
        (
            "",
            ValueError,
            "symbol must not be empty",
        ),
        (
            "   ",
            ValueError,
            "symbol must not be empty",
        ),
    ],
)
def test_pipeline_rejects_empty_symbol(
    symbol,
    expected_exception,
    expected_message,
) -> None:
    pipeline = create_pipeline()

    with pytest.raises(
        expected_exception,
        match=expected_message,
    ):
        pipeline.run(
            symbol=symbol
        )


@pytest.mark.parametrize(
    (
        "current_price",
        "expected_exception",
        "expected_message",
    ),
    [
        (
            True,
            TypeError,
            "current_price must be numeric",
        ),
        (
            "20000",
            TypeError,
            "current_price must be numeric",
        ),
        (
            0,
            ValueError,
            (
                "current_price must be greater "
                "than zero"
            ),
        ),
        (
            -1,
            ValueError,
            (
                "current_price must be greater "
                "than zero"
            ),
        ),
    ],
)
def test_pipeline_rejects_invalid_current_price(
    current_price,
    expected_exception,
    expected_message,
) -> None:
    pipeline = create_pipeline()

    with pytest.raises(
        expected_exception,
        match=expected_message,
    ):
        pipeline.run(
            symbol="AAA",
            current_price=current_price,
        )


def test_analyze_alias_calls_pipeline_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    provider_result = (
        create_success_provider_result()
    )

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        lambda **kwargs: provider_result,
    )

    result = pipeline.analyze(
        symbol="aaa",
        current_price=20_000.0,
    )

    assert result.symbol == "AAA"
    assert result.succeeded is True


def test_analyze_symbol_use_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    provider_result = (
        create_success_provider_result(
            symbol="FPT"
        )
    )

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        lambda **kwargs: provider_result,
    )

    result = analyze_symbol(
        pipeline=pipeline,
        symbol=" fpt ",
        current_price=20_000.0,
    )

    assert isinstance(
        result,
        AnalysisResult,
    )

    assert result.symbol == "FPT"
    assert result.succeeded is True


def test_analyze_symbol_rejects_none_pipeline(
) -> None:
    with pytest.raises(
        ValueError,
        match="pipeline must not be None",
    ):
        analyze_symbol(
            pipeline=None,
            symbol="AAA",
        )


def test_analyze_symbol_rejects_invalid_pipeline(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "pipeline must be an "
            "AnalysisPipeline"
        ),
    ):
        analyze_symbol(
            pipeline=object(),
            symbol="AAA",
        )


def test_analyze_and_explain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = create_pipeline()

    provider_result = (
        create_success_provider_result(
            symbol="MBB"
        )
    )

    monkeypatch.setattr(
        pipeline.statement_provider,
        "get",
        lambda **kwargs: provider_result,
    )

    result, explanation = (
        analyze_and_explain(
            pipeline=pipeline,
            symbol="MBB",
            current_price=20_000.0,
        )
    )

    assert isinstance(
        result,
        AnalysisResult,
    )

    assert isinstance(
        explanation,
        str,
    )

    assert result.succeeded is True

    assert (
        "DMI Analysis Pipeline"
        in explanation
    )

    assert "Symbol: MBB" in explanation
    assert "Success: True" in explanation
    assert "Financial Analysis:" in explanation
    assert "Weighted Valuation:" in explanation
    assert "Decision:" in explanation


def test_explain_result_rejects_none(
) -> None:
    pipeline = create_pipeline()

    with pytest.raises(
        ValueError,
        match="result must not be None",
    ):
        pipeline.explain_result(
            None
        )


def test_explain_result_rejects_invalid_type(
) -> None:
    pipeline = create_pipeline()

    with pytest.raises(
        TypeError,
        match=(
            "result must be an AnalysisResult"
        ),
    ):
        pipeline.explain_result(
            object()
        )