from dataclasses import dataclass, field


@dataclass(slots=True)
class DecisionResult:
    recommendation: str
    confidence: int
    stars: int
    summary: str
    reasons: list[str]
    risks: list[str]
    explanation: str | None = None

    def explain(self) -> str:
        if self.explanation:
            return self.explanation

        lines = [
            f"Decision: {self.recommendation}",
            f"Confidence: {self.confidence}%",
            "",
            "Reasons:",
        ]

        if self.reasons:
            lines.extend([f"- {reason}" for reason in self.reasons])
        else:
            lines.append("- No positive reasons provided.")

        lines.extend(["", "Risks:"])

        if self.risks:
            lines.extend([f"- {risk}" for risk in self.risks])
        else:
            lines.append("- No major risks identified.")

        return "\n".join(lines)