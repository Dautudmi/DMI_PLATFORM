from apps.portfolio.report import PortfolioReport
from presentation.markdown import MarkdownRenderer


def test_render_markdown():
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

    renderer = MarkdownRenderer()

    text = renderer.render(report)

    assert "# Portfolio Report - Demo" in text
    assert "**Health:** GOOD (82/100)" in text
    assert "Cash allocation is below target." in text
    assert "Increase cash allocation." in text