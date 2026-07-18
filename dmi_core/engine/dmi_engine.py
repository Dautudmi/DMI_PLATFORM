from dmi_core.analysis import FinancialAnalysis
from dmi_core.decision import DecisionEngine, DecisionPolicy
from dmi_core.engine.dmi_report import DMIReport
from dmi_core.models.financial_statement import FinancialStatement
from dmi_core.valuation import PEValuation, ValuationConfig


class DMIEngine:
    """
    Main facade of DMI Platform.

    This engine connects:
    FinancialStatement -> Analysis -> Valuation -> Decision -> Report
    """

    def __init__(
        self,
        valuation_config: ValuationConfig | None = None,
        decision_policy: DecisionPolicy | None = None,
    ):
        self.valuation_config = valuation_config or ValuationConfig()
        self.decision_policy = decision_policy or DecisionPolicy()

    def analyze(
        self,
        statement: FinancialStatement,
        current_price: float | None = None,
    ) -> DMIReport:

        analysis = FinancialAnalysis(statement).analyze()

        valuation = PEValuation(
            statement=statement,
            config=self.valuation_config,
        ).evaluate(
            current_price=current_price,
        )

        decision = DecisionEngine().evaluate(
            analysis=analysis,
            valuation=valuation,
            policy=self.decision_policy,
        )

        return DMIReport(
            symbol=statement.symbol,
            year=statement.year,
            quarter=statement.quarter,
            analysis=analysis,
            valuation=valuation,
            decision=decision,
        )