from __future__ import annotations

import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = Path(os.getenv("DATA_DIR", str(_ROOT / "data")))


def _load_words(language: str) -> dict[str, list[str]]:
    path = DATA_DIR / f"words_{language}.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return {"valid_guesses": payload.get("valid_guesses", []), "daily_answers": payload.get("daily_answers", [])}


def get_valid_guesses(language: str) -> list[str]:
    return _load_words(language)["valid_guesses"]


def get_daily_answers(language: str) -> list[str]:
    return _load_words(language)["daily_answers"]
