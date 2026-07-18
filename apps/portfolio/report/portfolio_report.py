from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class PortfolioReport:

    client_name: str

    health_level: str
    health_score: int

    highlights: list[str] = field(default_factory=list)

    suggested_actions: list[str] = field(default_factory=list)

    # ---------- Decision ----------

    decision: str | None = None

    confidence: int | None = None

    decision_explanation: str | None = None

    # ------------------------------

    generated_at: datetime = field(
        default_factory=datetime.now,
    )

    def to_markdown(self) -> str:

        lines = [
            f"# Portfolio Report - {self.client_name}",
            "",
            f"Health: **{self.health_level}** ({self.health_score}/100)",
        ]

        if self.decision:

            lines.extend(
                [
                    "",
                    "## Decision",
                    f"**{self.decision}**",
                ]
            )

            if self.confidence is not None:

                lines.append(
                    f"Confidence: {self.confidence}%"
                )

            if self.decision_explanation:

                lines.extend(
                    [
                        "",
                        self.decision_explanation,
                    ]
                )

        lines.extend(
            [
                "",
                "## Highlights",
            ]
        )

        if self.highlights:

            lines.extend(
                f"- {item}"
                for item in self.highlights
            )

        else:

            lines.append(
                "- No major highlights."
            )

        lines.extend(
            [
                "",
                "## Suggested Actions",
            ]
        )

        if self.suggested_actions:

            lines.extend(
                f"- {item}"
                for item in self.suggested_actions
            )

        else:

            lines.append(
                "- No immediate action required."
            )

        return "\n".join(lines)