from apps.portfolio.report import PortfolioReport
from presentation.telegram import TelegramRenderer


def test_render_telegram():

    report = PortfolioReport(
        client_name="Demo",
        health_level="GOOD",
        health_score=82,
        highlights=[
            "Cash allocation is below target.",
        ],
        suggested_actions=[
            "Increase cash allocation.",
        ],
    )

    renderer = TelegramRenderer()

    text = renderer.render(report)

    assert "DMI DAILY PORTFOLIO REPORT" in text
    assert "Demo" in text
    assert "GOOD (82/100)" in text
    assert "Cash allocation is below target." in text
    assert "Increase cash allocation." in text