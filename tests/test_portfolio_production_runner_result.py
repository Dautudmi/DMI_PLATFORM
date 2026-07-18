from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.models.portfolio_production_flow_result import (
    PortfolioProductionFlowResult,
)
from apps.portfolio.models.portfolio_production_runner_result import (
    PortfolioProductionRunnerResult,
)


@dataclass
class FakeTransaction:
    symbol: str


def create_transaction(
    symbol: str = "NAB",
) -> Any:
    return FakeTransaction(symbol=symbol)


def create_portfolio(
    client_name: str,
) -> Portfolio:
    return Portfolio(
        client_name=client_name,
        cash=0.0,
        holdings=[],
    )


def create_success_result(
    client_name: str,
) -> PortfolioProductionFlowResult:
    transaction = create_transaction()

    return PortfolioProductionFlowResult(
        success=True,
        transaction=transaction,
        portfolio=create_portfolio(
            client_name=client_name
        ),
        transaction_result=None,
        portfolio_file_path=(
            f"client_{client_name}.csv"
        ),
        report_text="PORTFOLIO REPORT",
        message="completed",
        error=None,
    )


def create_failure_result(
    client_name: str,
    error: str = "production flow failed",
) -> PortfolioProductionFlowResult:
    transaction = create_transaction()

    return PortfolioProductionFlowResult(
        success=False,
        transaction=transaction,
        portfolio=create_portfolio(
            client_name=client_name
        ),
        transaction_result=None,
        portfolio_file_path=None,
        report_text=None,
        message=None,
        error=error,
    )


def test_empty_result_is_successful() -> None:
    result = PortfolioProductionRunnerResult()

    assert result.results == ()
    assert result.total_count == 0
    assert result.success_count == 0
    assert result.failure_count == 0
    assert result.succeeded is True
    assert result.partially_succeeded is False
    assert result.failed is False
    assert result.successful_results == ()
    assert result.failed_results == ()
    assert result.message is None
    assert result.error is None


def test_all_successful_results() -> None:
    first_result = create_success_result(
        client_name="anh_dung"
    )

    second_result = create_success_result(
        client_name="chi_lan"
    )

    result = PortfolioProductionRunnerResult(
        results=(
            first_result,
            second_result,
        ),
        message="all clients completed",
    )

    assert result.total_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0
    assert result.succeeded is True
    assert result.partially_succeeded is False
    assert result.failed is False

    assert result.successful_results == (
        first_result,
        second_result,
    )

    assert result.failed_results == ()

    assert result.message == "all clients completed"
    assert result.error is None


def test_mixed_results_are_partially_successful() -> None:
    success_result = create_success_result(
        client_name="anh_dung"
    )

    failure_result = create_failure_result(
        client_name="chi_lan"
    )

    result = PortfolioProductionRunnerResult(
        results=(
            success_result,
            failure_result,
        )
    )

    assert result.total_count == 2
    assert result.success_count == 1
    assert result.failure_count == 1
    assert result.succeeded is False
    assert result.partially_succeeded is True
    assert result.failed is True

    assert result.successful_results == (
        success_result,
    )

    assert result.failed_results == (
        failure_result,
    )


def test_all_failed_results() -> None:
    first_result = create_failure_result(
        client_name="anh_dung"
    )

    second_result = create_failure_result(
        client_name="chi_lan"
    )

    result = PortfolioProductionRunnerResult(
        results=(
            first_result,
            second_result,
        )
    )

    assert result.total_count == 2
    assert result.success_count == 0
    assert result.failure_count == 2
    assert result.succeeded is False
    assert result.partially_succeeded is False
    assert result.failed is True

    assert result.successful_results == ()

    assert result.failed_results == (
        first_result,
        second_result,
    )


def test_runner_error_marks_result_as_failed() -> None:
    flow_result = create_success_result(
        client_name="anh_dung"
    )

    result = PortfolioProductionRunnerResult(
        results=(flow_result,),
        error="client registry unavailable",
    )

    assert result.total_count == 1
    assert result.success_count == 1
    assert result.failure_count == 0
    assert result.succeeded is False
    assert result.partially_succeeded is False
    assert result.failed is True
    assert (
        result.error
        == "client registry unavailable"
    )


def test_results_are_converted_to_tuple() -> None:
    flow_result = create_success_result(
        client_name="anh_dung"
    )

    result = PortfolioProductionRunnerResult(
        results=[flow_result],
    )

    assert isinstance(result.results, tuple)
    assert result.results == (flow_result,)


def test_rejects_invalid_result_item() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "results must contain only "
            "PortfolioProductionFlowResult"
        ),
    ):
        PortfolioProductionRunnerResult(
            results=("invalid result",)
        )


def test_normalizes_optional_text() -> None:
    result = PortfolioProductionRunnerResult(
        message="  completed  ",
        error="   ",
    )

    assert result.message == "completed"
    assert result.error is None


def test_get_result_by_client_name() -> None:
    first_result = create_success_result(
        client_name="anh_dung"
    )

    second_result = create_success_result(
        client_name="chi_lan"
    )

    result = PortfolioProductionRunnerResult(
        results=(
            first_result,
            second_result,
        )
    )

    found = result.get_result_by_client_name(
        "chi_lan"
    )

    assert found is second_result


def test_get_result_by_client_name_returns_none() -> None:
    flow_result = create_success_result(
        client_name="anh_dung"
    )

    result = PortfolioProductionRunnerResult(
        results=(flow_result,)
    )

    found = result.get_result_by_client_name(
        "not_found"
    )

    assert found is None


def test_get_result_by_client_name_rejects_empty_value() -> None:
    result = PortfolioProductionRunnerResult()

    with pytest.raises(
        ValueError,
        match="client_name must not be empty",
    ):
        result.get_result_by_client_name("   ")