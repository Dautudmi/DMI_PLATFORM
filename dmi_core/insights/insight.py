from dataclasses import dataclass, field

from dmi_core.insights.enums import (
    InsightCategory,
    InsightConfidence,
    InsightImpact,
    InsightSeverity,
)
from dmi_core.insights.evidence import Evidence


@dataclass(slots=True)
class Insight:
    """
    First-class business insight used across DMI Platform.

    Insight V2 is designed for:
    - prioritization
    - reasoning
    - recommendation
    - client advisory
    - AI copilot
    """

    category: InsightCategory
    title: str
    message: str

    severity: InsightSeverity = InsightSeverity.INFO
    confidence: InsightConfidence = InsightConfidence.MEDIUM
    impact: InsightImpact = InsightImpact.MEDIUM

    evidence: list[Evidence] = field(default_factory=list)

    suggested_action: str | None = None
    source: str | None = None
    tags: list[str] = field(default_factory=list)
    insight_id: str | None = None