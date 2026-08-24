from __future__ import annotations

from collections import Counter


MAX_WORD_LENGTH = 5


def normalize_word(word: str) -> str:
    return word.strip().lower().casefold()


def score_word(target: str, guess: str) -> list[int]:
    if len(target) != MAX_WORD_LENGTH or len(guess) != MAX_WORD_LENGTH:
        raise ValueError("Words must be exactly five characters long.")

    result = [0] * MAX_WORD_LENGTH
    remaining = Counter()

    for index, (target_char, guess_char) in enumerate(zip(target, guess)):
        if target_char == guess_char:
            result[index] = 2
        else:
            remaining[target_char] += 1

    for index, guess_char in enumerate(guess):
        if result[index] == 2:
            continue
        if remaining[guess_char] > 0:
            result[index] = 1
            remaining[guess_char] -= 1

    return result
