from dataclasses import dataclass

from dmi_core.policies.risk_profile import RiskProfile


@dataclass(slots=True)
class PortfolioPolicy:
    """
    Investment policy used to evaluate portfolio health.

    Metrics are objective.
    Health is policy-dependent.
    """

    risk_profile: RiskProfile = RiskProfile.BALANCED

    max_single_position: float = 0.25
    max_sector_weight: float = 0.35

    min_cash: float = 0.05
    max_cash: float = 0.30

    target_beta: float = 1.0

    @staticmethod
    def conservative() -> "PortfolioPolicy":
        return PortfolioPolicy(
            risk_profile=RiskProfile.CONSERVATIVE,
            max_single_position=0.15,
            max_sector_weight=0.25,
            min_cash=0.15,
            max_cash=0.45,
            target_beta=0.8,
        )

    @staticmethod
    def balanced() -> "PortfolioPolicy":
        return PortfolioPolicy()

    @staticmethod
    def growth() -> "PortfolioPolicy":
        return PortfolioPolicy(
            risk_profile=RiskProfile.GROWTH,
            max_single_position=0.30,
            max_sector_weight=0.45,
            min_cash=0.03,
            max_cash=0.25,
            target_beta=1.1,
        )

    @staticmethod
    def aggressive() -> "PortfolioPolicy":
        return PortfolioPolicy(
            risk_profile=RiskProfile.AGGRESSIVE,
            max_single_position=0.40,
            max_sector_weight=0.55,
            min_cash=0.00,
            max_cash=0.20,
            target_beta=1.3,
        )