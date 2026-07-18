from __future__ import annotations

from collections.abc import Mapping

from dmi_core.analysis.financial_analysis import (
    FinancialAnalysis,
)
from dmi_core.decision.decision_engine import (
    DecisionEngine,
)
from dmi_core.decision.decision_policy import (
    DecisionPolicy,
)
from dmi_core.evaluation.investment_evaluation_result import (
    InvestmentEvaluationResult,
)
from dmi_core.models.financial_statement import (
    FinancialStatement,
)
from dmi_core.valuation.valuation_engine import (
    ValuationEngine,
)


class InvestmentEvaluationEngine:
    """
    Orchestrate the complete investment evaluation pipeline.

    Flow:

        FinancialStatement
                │
                ├── FinancialAnalysis
                │       ↓
                │   FinancialAnalysisResult
                │
                ├── ValuationEngine
                │       ↓
                │   WeightedFairValueResult
                │
                └── DecisionEngine
                        ↓
                    DecisionResult
                        ↓
              InvestmentEvaluationResult

    Responsibility:
    - validate the input FinancialStatement
    - run financial analysis
    - run weighted valuation
    - run the final decision engine
    - return one aggregate result

    This engine does not:
    - calculate financial metrics directly
    - calculate PE or PB directly
    - calculate weighted fair value directly
    - contain decision-rule business logic
    """

    def __init__(
        self,
        valuation_engine: ValuationEngine | None = None,
        decision_engine: DecisionEngine | None = None,
        policy: DecisionPolicy | None = None,
        source: str = "DMI",
        schema_version: str = "1.0",
    ) -> None:
        """
        Create an InvestmentEvaluationEngine.

        Dependencies may be injected for:
        - testing
        - custom valuation registry
        - custom valuation assumptions
        - custom decision rules
        - custom decision policy
        """

        if valuation_engine is None:
            valuation_engine = ValuationEngine()

        if decision_engine is None:
            decision_engine = DecisionEngine()

        if policy is None:
            policy = DecisionPolicy()

        self._valuation_engine = valuation_engine
        self._decision_engine = decision_engine
        self._policy = policy

        self._source = self._normalize_required_text(
            value=source,
            field_name="source",
        )

        self._schema_version = self._normalize_required_text(
            value=schema_version,
            field_name="schema_version",
        )

    @property
    def valuation_engine(
        self,
    ) -> ValuationEngine:
        """
        Valuation engine used by this orchestrator.
        """

        return self._valuation_engine

    @property
    def decision_engine(
        self,
    ) -> DecisionEngine:
        """
        Decision engine used by this orchestrator.
        """

        return self._decision_engine

    @property
    def policy(
        self,
    ) -> DecisionPolicy:
        """
        Decision policy used by this orchestrator.
        """

        return self._policy

    @property
    def source(
        self,
    ) -> str:
        return self._source

    @property
    def schema_version(
        self,
    ) -> str:
        return self._schema_version

    def evaluate(
        self,
        statement: FinancialStatement,
        current_price: float | None = None,
        valuation_weights: Mapping[
            str,
            float,
        ] | None = None,
        continue_on_valuation_error: bool = True,
        policy: DecisionPolicy | None = None,
    ) -> InvestmentEvaluationResult:
        """
        Run the complete investment evaluation pipeline.

        Parameters
        ----------
        statement:
            DMI FinancialStatement aggregate.

        current_price:
            Current market price used for valuation metrics.

        valuation_weights:
            Optional valuation-method weights.

            Example:

                {
                    "PE": 0.60,
                    "PB": 0.40,
                }

            Weights do not need to total 1 because
            WeightedFairValueEngine normalizes them.

        continue_on_valuation_error:
            When True, a failed valuation model is converted into
            an N/A valuation component and the remaining models
            continue to run.

            When False, the original valuation exception is raised.

        policy:
            Optional policy override for this evaluation only.

            When omitted, the policy configured in the constructor
            is used.
        """

        self._validate_statement(
            statement
        )

        self._validate_current_price(
            current_price
        )

        resolved_policy = self._resolve_policy(
            policy
        )

        analysis = FinancialAnalysis(
            statement
        ).analyze()

        valuation = (
            self._valuation_engine.evaluate_weighted(
                statement=statement,
                current_price=current_price,
                weights=valuation_weights,
                continue_on_error=(
                    continue_on_valuation_error
                ),
            )
        )

        decision = self._decision_engine.evaluate(
            analysis=analysis,
            valuation=valuation,
            policy=resolved_policy,
        )

        return InvestmentEvaluationResult(
            symbol=self._resolve_symbol(
                statement
            ),
            analysis=analysis,
            valuation=valuation,
            decision=decision,
            current_price=current_price,
            source=self._source,
            schema_version=self._schema_version,
        )

    def _resolve_policy(
        self,
        policy: DecisionPolicy | None,
    ) -> DecisionPolicy:
        if policy is None:
            return self._policy

        if not isinstance(
            policy,
            DecisionPolicy,
        ):
            raise TypeError(
                "policy must be a DecisionPolicy"
            )

        return policy

    def _resolve_symbol(
        self,
        statement: FinancialStatement,
    ) -> str:
        symbol = getattr(
            statement,
            "symbol",
            None,
        )

        return self._normalize_required_text(
            value=symbol,
            field_name="statement.symbol",
        ).upper()

    def _validate_statement(
        self,
        statement: FinancialStatement,
    ) -> None:
        if statement is None:
            raise ValueError(
                "statement must not be None"
            )

        if not isinstance(
            statement,
            FinancialStatement,
        ):
            raise TypeError(
                "statement must be a "
                "FinancialStatement"
            )

        if statement.balance_sheet is None:
            raise ValueError(
                "statement.balance_sheet "
                "must not be None"
            )

        if statement.income_statement is None:
            raise ValueError(
                "statement.income_statement "
                "must not be None"
            )

        self._validate_statement_consistency(
            statement
        )

    def _validate_statement_consistency(
        self,
        statement: FinancialStatement,
    ) -> None:
        statement_symbol = (
            self._normalize_required_text(
                value=statement.symbol,
                field_name="statement.symbol",
            ).upper()
        )

        balance_sheet_symbol = getattr(
            statement.balance_sheet,
            "symbol",
            None,
        )

        income_statement_symbol = getattr(
            statement.income_statement,
            "symbol",
            None,
        )

        if balance_sheet_symbol is not None:
            normalized_balance_symbol = (
                self._normalize_required_text(
                    value=balance_sheet_symbol,
                    field_name=(
                        "balance_sheet.symbol"
                    ),
                ).upper()
            )

            if (
                normalized_balance_symbol
                != statement_symbol
            ):
                raise ValueError(
                    "balance_sheet.symbol does not "
                    "match statement.symbol"
                )

        if income_statement_symbol is not None:
            normalized_income_symbol = (
                self._normalize_required_text(
                    value=income_statement_symbol,
                    field_name=(
                        "income_statement.symbol"
                    ),
                ).upper()
            )

            if (
                normalized_income_symbol
                != statement_symbol
            ):
                raise ValueError(
                    "income_statement.symbol does not "
                    "match statement.symbol"
                )

        if (
            statement.balance_sheet.year
            != statement.year
        ):
            raise ValueError(
                "balance_sheet.year does not "
                "match statement.year"
            )

        if (
            statement.income_statement.year
            != statement.year
        ):
            raise ValueError(
                "income_statement.year does not "
                "match statement.year"
            )

        if (
            statement.balance_sheet.quarter
            != statement.quarter
        ):
            raise ValueError(
                "balance_sheet.quarter does not "
                "match statement.quarter"
            )

        if (
            statement.income_statement.quarter
            != statement.quarter
        ):
            raise ValueError(
                "income_statement.quarter does not "
                "match statement.quarter"
            )

    def _validate_current_price(
        self,
        current_price: float | None,
    ) -> None:
        if current_price is None:
            return

        if isinstance(
            current_price,
            bool,
        ):
            raise TypeError(
                "current_price must be numeric"
            )

        if not isinstance(
            current_price,
            (int, float),
        ):
            raise TypeError(
                "current_price must be numeric"
            )

        if current_price <= 0:
            raise ValueError(
                "current_price must be greater than zero"
            )

    def _normalize_required_text(
        self,
        value: object,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized_value = str(
            value
        ).strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized_value