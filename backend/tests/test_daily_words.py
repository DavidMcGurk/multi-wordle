from datetime import date

from backend.words.daily import daily_word


def test_daily_word_is_stable_for_same_date() -> None:
    assert daily_word('en', date(2025, 1, 1)) == daily_word('en', date(2025, 1, 1))


def test_daily_word_changes_for_consecutive_dates() -> None:
    assert daily_word('en', date(2025, 1, 1)) != daily_word('en', date(2025, 1, 2))


def test_languages_have_independent_schedules() -> None:
    assert daily_word('en', date(2025, 1, 3)) != daily_word('hu', date(2025, 1, 3))


def test_timezone_changes_do_not_change_result() -> None:
    assert daily_word('en', '2025-01-01') == daily_word('en', date(2025, 1, 1))
