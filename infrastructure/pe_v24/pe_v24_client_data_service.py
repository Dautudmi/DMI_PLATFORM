from typing import Any

from infrastructure.pe_v24.pe_v24_client_data_result import (
    PEV24ClientDataResult,
)


class PEV24ClientDataService:
    """
    Orchestration service kết hợp:

    - Client Registry Repository
    - Client Portfolio Repository

    Responsibility:
    - tìm client trong client_config.csv
    - đọc file client_<client_id>.csv
    - trả về cấu hình và danh mục của một khách

    Không chứa business logic portfolio.
    Không tính Health.
    Không tính Recommendation.
    Không render.
    """

    def __init__(
        self,
        client_registry_repository: Any,
        client_portfolio_repository: Any,
    ):
        if client_registry_repository is None:
            raise ValueError(
                "client_registry_repository must not be None"
            )

        if client_portfolio_repository is None:
            raise ValueError(
                "client_portfolio_repository must not be None"
            )

        self._client_registry_repository = client_registry_repository
        self._client_portfolio_repository = client_portfolio_repository

    def load_client_data(
        self,
        client_id: str,
    ) -> PEV24ClientDataResult:
        if client_id is None or not str(client_id).strip():
            raise ValueError("client_id must not be empty")

        normalized_client_id = str(client_id).strip()

        try:
            client_config = (
                self._client_registry_repository.require_by_id(
                    normalized_client_id
                )
            )

            positions = (
                self._client_portfolio_repository.load_portfolio(
                    normalized_client_id
                )
            )

            return PEV24ClientDataResult(
                success=True,
                client_id=normalized_client_id,
                client_config=client_config,
                positions=positions,
                error=None,
            )

        except Exception as exc:
            return PEV24ClientDataResult(
                success=False,
                client_id=normalized_client_id,
                client_config=None,
                positions=None,
                error=str(exc),
            )