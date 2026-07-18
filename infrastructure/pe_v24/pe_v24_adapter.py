from infrastructure.pe_v24.pe_v24_adapter_result import PEV24AdapterResult
from infrastructure.pe_v24.pe_v24_cafef_repository import PEV24CafeFRepository


class PEV24Adapter:
    """
    PE_V2.4 Adapter Foundation.

    Responsibility:
    - kiểm tra DMI có đọc được dữ liệu từ PE_V2.4 không
    - trả về kết quả tổng quan cho Application/Integration layer

    Không thay thế PE_V2.4 pipeline.
    Không tính recommendation.
    Không ghi file.
    """

    def __init__(self, cafef_repository: PEV24CafeFRepository):
        if cafef_repository is None:
            raise ValueError("cafef_repository must not be None")

        self._cafef_repository = cafef_repository

    def inspect(self) -> PEV24AdapterResult:
        try:
            rows = self._cafef_repository.load_rows()
            symbols = self._cafef_repository.load_symbols()

            return PEV24AdapterResult(
                success=True,
                total_rows=len(rows),
                total_symbols=len(symbols),
                data={
                    "rows": rows,
                    "symbols": symbols,
                },
                error=None,
            )

        except Exception as exc:
            return PEV24AdapterResult(
                success=False,
                total_rows=0,
                total_symbols=0,
                data=None,
                error=str(exc),
            )