from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from wordfreq import iter_wordlist

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TARGET_GUESS_COUNT = 5000
TARGET_ANSWER_COUNT = 1000


def _normalize_candidate(candidate: str) -> str | None:
    normalized = unicodedata.normalize('NFKD', candidate.lower().strip())
    stripped = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    if not re.fullmatch(r"[a-z]{5}", stripped):
        return None
    return stripped


def extract_5_letter_ascii_words(language: str, target_count: int = TARGET_GUESS_COUNT) -> list[str]:
    words: list[str] = []
    seen: set[str] = set()
    for candidate in iter_wordlist(language):
        normalized = _normalize_candidate(candidate)
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        words.append(normalized)
        if len(words) >= target_count:
            break
    return words


def main() -> None:
    raw_lists = {language: extract_5_letter_ascii_words(language, TARGET_GUESS_COUNT) for language in ("en", "hu")}
    common_target = min(len(raw_lists["en"]), len(raw_lists["hu"]))
    payloads: dict[str, dict[str, list[str]]] = {}
    for language in ("en", "hu"):
        valid_guesses = raw_lists[language][:common_target]
        answer_limit = min(TARGET_ANSWER_COUNT, len(valid_guesses))
        payloads[language] = {
            "valid_guesses": valid_guesses,
            "daily_answers": valid_guesses[:answer_limit],
        }

    for language, payload in payloads.items():
        with (DATA_DIR / f"words_{language}.json").open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")


if __name__ == "__main__":
    main()
