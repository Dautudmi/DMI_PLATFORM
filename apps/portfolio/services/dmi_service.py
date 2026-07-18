from dmi_core.engine import DMIEngine
from dmi_core.engine.dmi_report import DMIReport
from dmi_core.models.financial_statement import FinancialStatement


class DMIService:
    """
    Application adapter for DMIEngine.

    Apps Layer should use this service instead of calling
    DMIEngine directly.
    """

    def __init__(
        self,
        engine: DMIEngine | None = None,
    ) -> None:
        self._engine = engine or DMIEngine()

    def analyze(
        self,
        statement: FinancialStatement,
        current_price: float | None = None,
    ) -> DMIReport:

        return self._engine.analyze(
            statement=statement,
            current_price=current_price,
        )