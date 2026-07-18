from datetime import datetime
from datetime import date

from infrastructure.system_clock import SystemClock


def test_now():
    clock = SystemClock()

    assert isinstance(clock.now(), datetime)


def test_today():
    clock = SystemClock()

    assert isinstance(clock.today(), date)