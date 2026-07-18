from enum import Enum


class InsightCategory(str, Enum):
    ALLOCATION = "allocation"
    RISK = "risk"
    VALUATION = "valuation"
    QUALITY = "quality"
    MOMENTUM = "momentum"
    CASH = "cash"
    PORTFOLIO = "portfolio"
    MARKET = "market"
    MACRO = "macro"


class InsightSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class InsightConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InsightImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"