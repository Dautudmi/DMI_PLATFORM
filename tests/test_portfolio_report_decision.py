from apps.portfolio.report import PortfolioReport


def test_portfolio_report_contains_decision():

    report = PortfolioReport(
        client_name="Demo",

        health_level="GOOD",

        health_score=85,

        decision="BUY",

        confidence=92,

        decision_explanation="Excellent financial quality.",

        highlights=[],

        suggested_actions=[],
    )

    markdown = report.to_markdown()

    assert "Decision" in markdown

    assert "BUY" in markdown

    assert "92%" in markdown

    assert "Excellent financial quality." in markdown