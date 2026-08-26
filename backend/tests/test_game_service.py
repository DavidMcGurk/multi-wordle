from backend.game.manager import GameManager
from backend.game.scoring import score_word
from backend.game.state import GameStatus, Language


def test_create_and_join_game() -> None:
    manager = GameManager()
    game = manager.create_game('alice', 'session-1')
    assert game.code
    joined = manager.join_game(game.code, 'bob', 'session-2')
    assert len(joined.players) == 2


def test_ready_and_start_game() -> None:
    manager = GameManager()
    game = manager.create_game('alice', 'session-1')
    manager.join_game(game.code, 'bob', 'session-2')
    manager.update_player_language(game, game.players[0].id, 'en')
    manager.update_player_language(game, game.players[1].id, 'hu')
    manager.ready_player(game, game.players[0].id)
    manager.ready_player(game, game.players[1].id)
    manager.set_target_words(game)
    assert game.status == GameStatus.IN_PROGRESS


def test_guessing_and_winning() -> None:
    manager = GameManager()
    game = manager.create_game('alice', 'session-1')
    game = manager.join_game(game.code, 'bob', 'session-2')
    game.players[0].language = Language.EN
    game.players[1].language = Language.HU
    game.players[0].ready = True
    game.players[1].ready = True
    game.status = GameStatus.IN_PROGRESS
    game.target_words = {game.players[0].id: 'about', game.players[1].id: 'asztal'}
    payload = manager.submit_guess(game, game.players[0].id, 'about')
    assert payload['correct'] is True
    assert game.status == GameStatus.IN_PROGRESS
    assert game.winner_id == game.players[0].id


def test_guess_must_be_in_valid_word_list() -> None:
    manager = GameManager()
    game = manager.create_game('alice', 'session-1')
    game = manager.join_game(game.code, 'bob', 'session-2')
    game.players[0].language = Language.EN
    game.players[1].language = Language.HU
    game.status = GameStatus.IN_PROGRESS
    game.target_words = {game.players[0].id: 'about', game.players[1].id: 'asztal'}

    try:
        manager.submit_guess(game, game.players[0].id, 'zzzzz')
        raise AssertionError('Expected invalid word to be rejected')
    except ValueError as exc:
        assert str(exc) == 'word not in valid answers list'


def test_sixth_guess_reveals_answer() -> None:
    manager = GameManager()
    game = manager.create_game('alice', 'session-1')
    game = manager.join_game(game.code, 'bob', 'session-2')
    game.players[0].language = Language.EN
    game.players[1].language = Language.HU
    game.status = GameStatus.IN_PROGRESS
    game.target_words = {game.players[0].id: 'about', game.players[1].id: 'asztal'}

    for guess in ['great', 'these', 'where', 'whole', 'heard']:
        manager.submit_guess(game, game.players[0].id, guess)

    payload = manager.submit_guess(game, game.players[0].id, 'under')
    assert payload['correct'] is False
    assert game.status == GameStatus.IN_PROGRESS
    assert payload['target_word'] == 'about'


def test_tracks_best_progress_and_winner_timestamp() -> None:
    manager = GameManager()
    game = manager.create_game('alice', 'session-1')
    game = manager.join_game(game.code, 'bob', 'session-2')
    game.players[0].language = Language.EN
    game.players[1].language = Language.HU
    game.status = GameStatus.IN_PROGRESS
    game.target_words = {game.players[0].id: 'about', game.players[1].id: 'asztal'}

    first = manager.submit_guess(game, game.players[0].id, 'after')
    assert first['best_progress'] == [2, 1, 0, 0, 0]
    assert first['winner_decided_at'] is None

    win = manager.submit_guess(game, game.players[0].id, 'about')
    assert win['correct'] is True
    assert win['best_progress'] == [2, 2, 2, 2, 2]
    assert win['winner_decided_at'] is not None
    assert game.winner_id == game.players[0].id


def test_duplicate_letter_example_counts_only_three_matches() -> None:
    scored = score_word('trust', 'stark')
    assert scored == [1, 1, 0, 1, 0]
    assert sum(1 for value in scored if value > 0) == 3
