from datetime import datetime, date


class SystemClock:
    """
    System clock infrastructure.
    """

    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return date.today()