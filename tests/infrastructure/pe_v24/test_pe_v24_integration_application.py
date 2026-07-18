from infrastructure.pe_v24.pe_v24_integration_application import (
    PEV24IntegrationApplication,
)


class FakeClientRepository:
    def load_clients(self):
        return ["client_a", "client_b"]


class FakePortfolioRepository:
    def load_holdings(self):
        return ["holding_a", "holding_b", "holding_c"]


class FakeBuyCandidateRepository:
    def load_candidates(self):
        return ["FPT", "HPG"]


class FakeStrategyRepository:
    def load_strategies(self):
        return ["BUY_V1"]


def test_pe_v24_integration_application_requires_client_repository():
    try:
        PEV24IntegrationApplication(
            client_repository=None,
            portfolio_repository=FakePortfolioRepository(),
            buy_candidate_repository=FakeBuyCandidateRepository(),
            strategy_repository=FakeStrategyRepository(),
        )
    except ValueError as exc:
        assert str(exc) == "client_repository must not be None"
    else:
        assert False


def test_pe_v24_integration_application_requires_portfolio_repository():
    try:
        PEV24IntegrationApplication(
            client_repository=FakeClientRepository(),
            portfolio_repository=None,
            buy_candidate_repository=FakeBuyCandidateRepository(),
            strategy_repository=FakeStrategyRepository(),
        )
    except ValueError as exc:
        assert str(exc) == "portfolio_repository must not be None"
    else:
        assert False


def test_pe_v24_integration_application_requires_buy_candidate_repository():
    try:
        PEV24IntegrationApplication(
            client_repository=FakeClientRepository(),
            portfolio_repository=FakePortfolioRepository(),
            buy_candidate_repository=None,
            strategy_repository=FakeStrategyRepository(),
        )
    except ValueError as exc:
        assert str(exc) == "buy_candidate_repository must not be None"
    else:
        assert False


def test_pe_v24_integration_application_requires_strategy_repository():
    try:
        PEV24IntegrationApplication(
            client_repository=FakeClientRepository(),
            portfolio_repository=FakePortfolioRepository(),
            buy_candidate_repository=FakeBuyCandidateRepository(),
            strategy_repository=None,
        )
    except ValueError as exc:
        assert str(exc) == "strategy_repository must not be None"
    else:
        assert False


def test_pe_v24_integration_application_inspect_success():
    app = PEV24IntegrationApplication(
        client_repository=FakeClientRepository(),
        portfolio_repository=FakePortfolioRepository(),
        buy_candidate_repository=FakeBuyCandidateRepository(),
        strategy_repository=FakeStrategyRepository(),
    )

    result = app.inspect()

    assert result.success is True
    assert result.total_clients == 2
    assert result.total_holdings == 3
    assert result.total_buy_candidates == 2
    assert result.total_strategies == 1
    assert result.error is None
    assert result.data["clients"] == ["client_a", "client_b"]


def test_pe_v24_integration_application_returns_failed_when_client_repo_invalid():
    class InvalidClientRepository:
        pass

    app = PEV24IntegrationApplication(
        client_repository=InvalidClientRepository(),
        portfolio_repository=FakePortfolioRepository(),
        buy_candidate_repository=FakeBuyCandidateRepository(),
        strategy_repository=FakeStrategyRepository(),
    )

    result = app.inspect()

    assert result.success is False
    assert result.error == "client_repository must have load_clients method"


def test_pe_v24_integration_application_returns_failed_when_portfolio_repo_invalid():
    class InvalidPortfolioRepository:
        pass

    app = PEV24IntegrationApplication(
        client_repository=FakeClientRepository(),
        portfolio_repository=InvalidPortfolioRepository(),
        buy_candidate_repository=FakeBuyCandidateRepository(),
        strategy_repository=FakeStrategyRepository(),
    )

    result = app.inspect()

    assert result.success is False
    assert result.error == "portfolio_repository must have load_holdings method"


def test_pe_v24_integration_application_returns_failed_when_buy_candidate_repo_invalid():
    class InvalidBuyCandidateRepository:
        pass

    app = PEV24IntegrationApplication(
        client_repository=FakeClientRepository(),
        portfolio_repository=FakePortfolioRepository(),
        buy_candidate_repository=InvalidBuyCandidateRepository(),
        strategy_repository=FakeStrategyRepository(),
    )

    result = app.inspect()

    assert result.success is False
    assert (
        result.error
        == "buy_candidate_repository must have load_candidates method"
    )


def test_pe_v24_integration_application_returns_failed_when_strategy_repo_invalid():
    class InvalidStrategyRepository:
        pass

    app = PEV24IntegrationApplication(
        client_repository=FakeClientRepository(),
        portfolio_repository=FakePortfolioRepository(),
        buy_candidate_repository=FakeBuyCandidateRepository(),
        strategy_repository=InvalidStrategyRepository(),
    )

    result = app.inspect()

    assert result.success is False
    assert result.error == "strategy_repository must have load_strategies method"


def test_pe_v24_integration_application_returns_failed_when_repo_raises():
    class FailingClientRepository:
        def load_clients(self):
            raise RuntimeError("client repo failed")

    app = PEV24IntegrationApplication(
        client_repository=FailingClientRepository(),
        portfolio_repository=FakePortfolioRepository(),
        buy_candidate_repository=FakeBuyCandidateRepository(),
        strategy_repository=FakeStrategyRepository(),
    )

    result = app.inspect()

    assert result.success is False
    assert result.total_clients == 0
    assert result.total_holdings == 0
    assert result.total_buy_candidates == 0
    assert result.total_strategies == 0
    assert result.data is None
    assert result.error == "client repo failed"