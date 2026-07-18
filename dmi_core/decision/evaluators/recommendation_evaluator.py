from dmi_core.decision.decision_policy import DecisionPolicy


class RecommendationEvaluator:
    """
    Evaluate investment recommendation based on financial score
    and margin of safety.
    """

    @staticmethod
    def evaluate(
        score: float,
        margin_of_safety: float | None,
        policy: DecisionPolicy,
    ) -> tuple[str, int]:

        mos = margin_of_safety or 0

        if (
            score >= policy.min_score_buy
            and mos >= policy.min_margin_of_safety
        ):
            return "STRONG BUY", policy.strong_buy_stars

        if score >= 70 and mos >= 10:
            return "BUY", policy.buy_stars

        if score >= policy.min_score_watch:
            return "WATCH", policy.watch_stars

        return "SELL", policy.sell_stars