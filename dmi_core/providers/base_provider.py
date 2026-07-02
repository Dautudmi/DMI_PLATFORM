from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Base class cho mọi nguồn dữ liệu của DMI.

    CafeF, FireAnt, FiinPro sau này đều phải tuân theo interface này.
    """

    @abstractmethod
    def get_balance_sheet(self, symbol: str, period: str = "NAM", page_size: int = 4):
        pass

    @abstractmethod
    def get_income_statement(self, symbol: str, period: str = "NAM", page_size: int = 4):
        pass