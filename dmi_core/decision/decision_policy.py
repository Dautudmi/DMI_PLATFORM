from dataclasses import dataclass


@dataclass(slots=True)
class DecisionPolicy:
    """
    Configuration for investment decision rules.

    Margin of Safety uses ratio format:

        0.10 = 10%
        0.15 = 15%
        0.25 = 25%
    """

    # STRONG BUY thresholds
    min_score_buy: int = 80
    min_margin_of_safety: float = 0.15

    # BUY thresholds
    min_score_regular_buy: int = 70
    min_margin_of_safety_buy: float = 0.10

    # WATCH threshold
    min_score_watch: int = 60

    max_debt_equity: float = 1.5

    strong_buy_stars: int = 5
    buy_stars: int = 4
    watch_stars: int = 3
    sell_stars: int = 2