from __future__ import annotations

import time
from typing import Any

from backend.game.manager import GameManager
from backend.game.state import Game, GameStatus, Language

manager = GameManager()


def create_game(player_name: str, session_token: str, language: str | None = None) -> Game:
    return manager.create_game(player_name, session_token, language)


def join_game(code: str, player_name: str, session_token: str, language: str | None = None) -> Game:
    return manager.join_game(code, player_name, session_token, language)


def choose_language(code: str, player_id: str, language: str) -> Game:
    game = manager.get_game(code)
    if game is None:
        raise ValueError("Game not found")
    manager.update_player_language(game, player_id, language)
    return game


def ready_game(code: str, player_id: str) -> Game:
    game = manager.get_game(code)
    if game is None:
        raise ValueError("Game not found")
    manager.ready_player(game, player_id)
    if all(player.ready for player in game.players):
        manager.set_target_words(game)
    return game


def submit_guess(code: str, player_id: str, guess: str) -> dict[str, Any]:
    game = manager.get_game(code)
    if game is None:
        raise ValueError("Game not found")
    payload = manager.submit_guess(game, player_id, guess)
    return payload


def get_game_state(code: str) -> Game | None:
    return manager.get_game(code)


def disconnect_player(code: str, player_id: str) -> Game | None:
    game = manager.get_game(code)
    if game is not None:
        manager.disconnect_player(game, player_id)
    return game


def reconnect_player(code: str, player_id: str) -> Game | None:
    game = manager.get_game(code)
    if game is not None:
        manager.reconnect_player(game, player_id)
    return game
