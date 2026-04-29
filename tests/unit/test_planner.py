from datetime import datetime, timezone

from elon.content.planner import DEFAULT_CADENCE, _platforms_for_today, next_slot


class _T:
    def __init__(self, settings=None):
        self.settings_json = settings or {}


def test_default_cadence_weekdays():
    # Monday (0): IG + TT + FB; Tuesday (1): IG + TT only.
    monday = _platforms_for_today(DEFAULT_CADENCE, 0)
    assert set(monday) == {"ig", "tiktok", "fb"}
    tuesday = _platforms_for_today(DEFAULT_CADENCE, 1)
    assert set(tuesday) == {"ig", "tiktok"}


def test_next_slot_picks_future_day():
    after = datetime(2026, 4, 28, 14, 0, tzinfo=timezone.utc)  # Tue 14:00
    slot = next_slot(_T(), "fb", after=after)
    # Default FB cadence: Mon/Wed/Fri. Next valid is Wednesday.
    assert slot.weekday() == 2
    assert slot > after


def test_next_slot_today_if_hour_later():
    after = datetime(2026, 4, 27, 9, 0, tzinfo=timezone.utc)  # Mon 09:00
    slot = next_slot(_T({"post_hour_utc": 14}), "fb", after=after)
    # FB allowed Monday; default post hour 14:00 is later than 09:00 → today.
    assert slot.weekday() == 0
    assert slot.hour == 14
