from abc import ABC, abstractmethod

from dmi_core.models.analysis_result import AnalysisResult


class BaseRule(ABC):
    """
    Base class for all DMI financial rules.

    A rule receives metric values and returns an AnalysisResult.
    """

    @staticmethod
    @abstractmethod
    def evaluate(*args, **kwargs) -> AnalysisResult:
        """
        Evaluate financial metrics and return AnalysisResult.
        """
        raise NotImplementedError