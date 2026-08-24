from __future__ import annotations

import hashlib
import random
from datetime import date, datetime, timezone

from backend.game.state import Language
from backend.words.repository import get_daily_answers

EPOCH = date(2024, 1, 1)


def _utc_date(date_value: date | str | None = None) -> date:
    if date_value is None:
        return datetime.now(timezone.utc).date()
    if isinstance(date_value, date):
        return date_value
    return datetime.fromisoformat(date_value).date()


def daily_word(language: str | Language, date_value: date | str | None = None) -> str:
    if isinstance(language, Language):
        language_name = language.value
    else:
        language_name = str(language).split(".")[-1].lower()
    normalized_date = _utc_date(date_value)
    day_index = (normalized_date - EPOCH).days
    answers = get_daily_answers(language_name)
    if not answers:
        raise ValueError(f"No words configured for language {language_name}")
    seed = hashlib.sha256(f"{language_name}:{day_index}".encode("utf-8")).digest()
    rng = random.Random(seed.hex())
    ordered = list(answers)
    rng.shuffle(ordered)
    return ordered[day_index % len(ordered)]
