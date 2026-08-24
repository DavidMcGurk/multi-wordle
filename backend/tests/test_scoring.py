from backend.game.scoring import score_word


def test_correct_letters_are_marked() -> None:
    assert score_word('apple', 'apple') == [2, 2, 2, 2, 2]


def test_present_letters_are_marked() -> None:
    assert score_word('stone', 'sugar') == [2, 0, 0, 0, 0]


def test_repeated_letters_are_handled() -> None:
    assert score_word('level', 'eerie') == [1, 2, 0, 0, 0]


def test_hungarian_accents_are_preserved() -> None:
    assert score_word('erdőn', 'őrdőn') == [0, 2, 2, 2, 2]
