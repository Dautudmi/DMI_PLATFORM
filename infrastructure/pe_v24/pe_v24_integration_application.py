from typing import Any

from infrastructure.pe_v24.pe_v24_integration_result import (
    PEV24IntegrationResult,
)


class PEV24IntegrationApplication:
    """
    PE_V2.4 Integration Application.

    Responsibility:
    - gom các PE repositories
    - kiểm tra DMI có đọc được dữ liệu PE_V2.4 không
    - trả về thống kê tổng quan

    Không thay thế pipeline PE cũ.
    Không tính BUY.
    Không tính Health.
    Không render.
    Không gửi Telegram.
    """

    def __init__(
        self,
        client_repository: Any,
        portfolio_repository: Any,
        buy_candidate_repository: Any,
        strategy_repository: Any,
    ):
        if client_repository is None:
            raise ValueError("client_repository must not be None")

        if portfolio_repository is None:
            raise ValueError("portfolio_repository must not be None")

        if buy_candidate_repository is None:
            raise ValueError("buy_candidate_repository must not be None")

        if strategy_repository is None:
            raise ValueError("strategy_repository must not be None")

        self._client_repository = client_repository
        self._portfolio_repository = portfolio_repository
        self._buy_candidate_repository = buy_candidate_repository
        self._strategy_repository = strategy_repository

    def inspect(self) -> PEV24IntegrationResult:
        try:
            clients = self._load_clients()
            holdings = self._load_holdings()
            buy_candidates = self._load_buy_candidates()
            strategies = self._load_strategies()

            return PEV24IntegrationResult(
                success=True,
                total_clients=len(clients),
                total_holdings=len(holdings),
                total_buy_candidates=len(buy_candidates),
                total_strategies=len(strategies),
                data={
                    "clients": clients,
                    "holdings": holdings,
                    "buy_candidates": buy_candidates,
                    "strategies": strategies,
                },
                error=None,
            )

        except Exception as exc:
            return PEV24IntegrationResult(
                success=False,
                total_clients=0,
                total_holdings=0,
                total_buy_candidates=0,
                total_strategies=0,
                data=None,
                error=str(exc),
            )

    def _load_clients(self):
        if hasattr(self._client_repository, "load_clients"):
            return self._client_repository.load_clients()

        raise AttributeError("client_repository must have load_clients method")

    def _load_holdings(self):
        if hasattr(self._portfolio_repository, "load_holdings"):
            return self._portfolio_repository.load_holdings()

        raise AttributeError("portfolio_repository must have load_holdings method")

    def _load_buy_candidates(self):
        if hasattr(self._buy_candidate_repository, "load_candidates"):
            return self._buy_candidate_repository.load_candidates()

        raise AttributeError(
            "buy_candidate_repository must have load_candidates method"
        )

    def _load_strategies(self):
        if hasattr(self._strategy_repository, "load_strategies"):
            return self._strategy_repository.load_strategies()

        raise AttributeError("strategy_repository must have load_strategies method")