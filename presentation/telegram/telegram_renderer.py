from apps.portfolio.report import PortfolioReport


class TelegramRenderer:
    """
    Render PortfolioReport into Telegram Markdown format.
    """

    def render(
        self,
        report: PortfolioReport,
    ) -> str:

        lines = [
            "📊 *DMI DAILY PORTFOLIO REPORT*",
            "",
            f"👤 *Client:* {report.client_name}",
            "",
            f"🩺 *Health:* {report.health_level} ({report.health_score}/100)",
            "",
            "📌 *Highlights*",
        ]

        if report.highlights:
            lines.extend(
                f"• {item}"
                for item in report.highlights
            )
        else:
            lines.append("• No major highlights.")

        lines.extend(
            [
                "",
                "💡 *Suggested Actions*",
            ]
        )

        if report.suggested_actions:
            lines.extend(
                f"• {item}"
                for item in report.suggested_actions
            )
        else:
            lines.append("• No immediate action required.")

        return "\n".join(lines)