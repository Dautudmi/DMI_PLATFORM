from typing import Callable, Iterable, Any

from apps.portfolio.models.client_batch_result import (
    ClientBatchItemResult,
    ClientBatchResult,
)


class ClientBatchProcessor:
    """
    Process many clients safely.

    Responsibility:
    - nhận danh sách client_id
    - chạy từng client qua handler được truyền vào
    - client nào lỗi thì ghi nhận lỗi
    - không để một client lỗi làm dừng toàn bộ batch

    Không chứa business logic portfolio.
    Không render.
    Không gửi Telegram.
    Không đọc file.
    """

    def __init__(self, handler: Callable[[str], Any]):
        if handler is None:
            raise ValueError("handler must not be None")

        self._handler = handler

    def process(self, client_ids: Iterable[str]) -> ClientBatchResult:
        if client_ids is None:
            raise ValueError("client_ids must not be None")

        results: list[ClientBatchItemResult] = []

        for client_id in client_ids:
            normalized_client_id = self._normalize_client_id(client_id)

            if not normalized_client_id:
                results.append(
                    ClientBatchItemResult(
                        client_id=str(client_id),
                        success=False,
                        data=None,
                        error="client_id is empty",
                    )
                )
                continue

            try:
                data = self._handler(normalized_client_id)

                results.append(
                    ClientBatchItemResult(
                        client_id=normalized_client_id,
                        success=True,
                        data=data,
                        error=None,
                    )
                )

            except Exception as exc:
                results.append(
                    ClientBatchItemResult(
                        client_id=normalized_client_id,
                        success=False,
                        data=None,
                        error=str(exc),
                    )
                )

        success_count = sum(1 for item in results if item.success)
        failed_count = len(results) - success_count

        return ClientBatchResult(
            total_clients=len(results),
            success_count=success_count,
            failed_count=failed_count,
            results=results,
        )

    def _normalize_client_id(self, client_id: str) -> str:
        if client_id is None:
            return ""

        return str(client_id).strip()