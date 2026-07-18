from apps.portfolio.report import PortfolioReport


class MarkdownRenderer:
    """
    Render PortfolioReport as Markdown.
    """

    def render(
        self,
        report: PortfolioReport,
    ) -> str:

        lines = [
            f"# Portfolio Report - {report.client_name}",
            "",
            f"**Health:** {report.health_level} ({report.health_score}/100)",
            "",
            "## Highlights",
        ]

        if report.highlights:
            lines.extend(f"- {item}" for item in report.highlights)
        else:
            lines.append("- No major highlights.")

        lines.extend(
            [
                "",
                "## Suggested Actions",
            ]
        )

        if report.suggested_actions:
            lines.extend(f"- {item}" for item in report.suggested_actions)
        else:
            lines.append("- No immediate action required.")

        return "\n".join(lines)