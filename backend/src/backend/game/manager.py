from __future__ import annotations

import secrets
import time
import unicodedata
import uuid
from typing import Any

from backend.config import settings
from backend.game.state import Game, GameStatus, Language, Player
from backend.words.repository import get_valid_guesses


class GameManager:
    def __init__(self) -> None:
        self._games: dict[str, Game] = {}
        self._game_lookup: dict[str, Game] = {}
        self._lock = __import__("threading").RLock()

    def _generate_code(self) -> str:
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        return "".join(secrets.choice(alphabet) for _ in range(settings.join_code_length))

    def create_game(self, player_name: str, session_token: str, language: str | None = None) -> Game:
        with self._lock:
            code = self._generate_code()
            while code in self._games:
                code = self._generate_code()
            player = Player(id=str(uuid.uuid4()), session_token=session_token, name=player_name, is_connected=True)
            if language is not None:
                player.language = Language(language)
            game = Game(code=code, players=[player], status=GameStatus.WAITING_FOR_OPPONENT, created_at=time.time(), updated_at=time.time())
            self._games[code] = game
            self._game_lookup[player.id] = game
            return game

    def join_game(self, code: str, player_name: str, session_token: str, language: str | None = None) -> Game:
        with self._lock:
            game = self._games.get(code.upper())
            if game is None:
                raise ValueError("Game not found")
            if len(game.players) >= settings.max_players_per_game:
                raise ValueError("Game is full")
            if any(player.session_token == session_token for player in game.players):
                return game
            player = Player(id=str(uuid.uuid4()), session_token=session_token, name=player_name, is_connected=True)
            if language is not None:
                player.language = Language(language)
            game.players.append(player)
            game.status = GameStatus.READY
            if len(game.players) == settings.max_players_per_game and all(p.language is not None for p in game.players):
                self.set_target_words(game)
            else:
                game.updated_at = time.time()
            self._game_lookup[player.id] = game
            return game

    def get_game(self, code: str) -> Game | None:
        return self._games.get(code.upper())

    def get_player_game(self, player_id: str) -> Game | None:
        return self._game_lookup.get(player_id)

    def update_player_language(self, game: Game, player_id: str, language: str) -> None:
        with self._lock:
            player = next((p for p in game.players if p.id == player_id), None)
            if player is None:
                raise KeyError("Player not found")
            if game.status in {GameStatus.IN_PROGRESS, GameStatus.FINISHED}:
                raise ValueError("Language cannot be changed after the game starts")
            player.language = Language(language)
            game.updated_at = time.time()

    def ready_player(self, game: Game, player_id: str) -> None:
        with self._lock:
            player = next((p for p in game.players if p.id == player_id), None)
            if player is None:
                raise KeyError("Player not found")
            if player.ready:
                raise ValueError("Player is already ready")
            player.ready = True
            game.status = GameStatus.READY if game.status != GameStatus.COUNTDOWN else game.status
            if all(p.ready for p in game.players):
                game.status = GameStatus.COUNTDOWN
                game.started_at = time.time()
                game.updated_at = time.time()

    def set_target_words(self, game: Game) -> None:
        with self._lock:
            for player in game.players:
                if player.language is None:
                    raise ValueError("Each player must choose a language before the game starts")
                from backend.words.daily import daily_word
                game.target_words[player.id] = daily_word(player.language, None)
            game.status = GameStatus.IN_PROGRESS
            game.updated_at = time.time()

    def _maybe_finish_game(self, game: Game, timestamp: float) -> None:
        if game.started_at is not None and (timestamp - game.started_at) >= 600:
            game.status = GameStatus.FINISHED
            game.ended_at = timestamp
            winners = [player for player in game.players if player.outcome == 'won']
            if len(winners) == 1:
                game.winner_id = winners[0].id
                game.winner_decided_at = min(winners[0].resolved_at or timestamp, timestamp)
            elif len(winners) > 1:
                earliest = min(winners, key=lambda player: player.resolved_at or timestamp)
                game.winner_id = earliest.id
                game.winner_decided_at = earliest.resolved_at or timestamp
            else:
                game.winner_id = None
                game.winner_decided_at = timestamp
            return

        if len(game.players) < 2:
            return

        resolved_players = [player for player in game.players if player.outcome is not None]
        if len(resolved_players) != len(game.players):
            return

        winners = [player for player in game.players if player.outcome == 'won']
        game.status = GameStatus.FINISHED
        game.ended_at = timestamp
        if len(winners) == 1:
            game.winner_id = winners[0].id
            game.winner_decided_at = winners[0].resolved_at or timestamp
        elif len(winners) > 1:
            earliest = min(winners, key=lambda player: player.resolved_at or timestamp)
            game.winner_id = earliest.id
            game.winner_decided_at = earliest.resolved_at or timestamp
        else:
            game.winner_id = None
            game.winner_decided_at = timestamp

    def submit_guess(self, game: Game, player_id: str, guess: str) -> dict[str, Any]:
        with self._lock:
            player = next((p for p in game.players if p.id == player_id), None)
            if player is None:
                raise KeyError("Player not found")
            if game.status not in {GameStatus.IN_PROGRESS, GameStatus.COUNTDOWN}:
                raise ValueError("Game is not in progress")
            if player.language is None:
                raise ValueError("Player language is required")
            normalized = unicodedata.normalize('NFC', guess.strip()).lower()
            if len(normalized) != 5:
                raise ValueError("Guess must be exactly 5 characters")
            valid_words = set(get_valid_guesses(player.language.value))
            if normalized not in valid_words:
                raise ValueError("word not in valid answers list")
            if normalized in player.guesses:
                raise ValueError("Duplicate guess")
            if len(player.guesses) >= settings.max_guesses_per_game:
                raise ValueError("You have used all 6 guesses.")

            target = game.target_words[player.id]
            from backend.game.scoring import score_word
            result = score_word(target, normalized)
            sorted_result = sorted(result, reverse=True)
            player.guesses.append(normalized)
            player.total_guesses = len(player.guesses)
            if not player.best_progress:
                player.best_progress = sorted_result
            else:
                player.best_progress = [max(player.best_progress[index], sorted_result[index]) for index in range(5)]
            timestamp = time.time()
            game.updated_at = timestamp

            if normalized == target:
                player.won = True
                player.outcome = 'won'
                player.resolved_at = timestamp
            elif len(player.guesses) >= settings.max_guesses_per_game:
                player.won = False
                player.outcome = 'lost'
                player.resolved_at = timestamp
            elif player.outcome is None:
                player.won = False

            if game.winner_id is None and player.outcome == 'won':
                game.winner_id = player.id
                game.winner_decided_at = timestamp

            self._maybe_finish_game(game, timestamp)

            return {
                "correct": normalized == target,
                "result": result,
                "guess_count": len(player.guesses),
                "winner_id": game.winner_id,
                "winner_decided_at": game.winner_decided_at,
                "player_id": player.id,
                "target_word": target if (game.status == GameStatus.FINISHED or player.outcome == 'lost') else None,
                "best_progress": player.best_progress,
            }

    def disconnect_player(self, game: Game, player_id: str) -> None:
        with self._lock:
            player = next((p for p in game.players if p.id == player_id), None)
            if player is not None:
                player.is_connected = False
            game.updated_at = time.time()

    def reconnect_player(self, game: Game, player_id: str) -> None:
        with self._lock:
            player = next((p for p in game.players if p.id == player_id), None)
            if player is not None:
                player.is_connected = True
            game.updated_at = time.time()

    def list_games(self) -> list[Game]:
        return list(self._games.values())
