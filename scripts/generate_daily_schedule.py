from __future__ import annotations

from datetime import date

from backend.words.daily import daily_word

if __name__ == "__main__":
    sample_days = [date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 3)]
    for language in ("en", "hu"):
        for day in sample_days:
            print(language, day.isoformat(), daily_word(language, day))
