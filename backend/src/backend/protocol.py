from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ClientMessageType = Literal["join_game", "ready", "guess", "leave"]
ServerMessageType = Literal["game_state", "player_joined", "player_ready", "game_started", "guess_result", "opponent_progress", "game_finished", "error"]


@dataclass(slots=True)
class JoinGameMessage:
    type: Literal["join_game"]
    code: str | None = None
    player_name: str | None = None
    session_token: str | None = None
    language: str | None = None


@dataclass(slots=True)
class ReadyMessage:
    type: Literal["ready"]
    language: str


@dataclass(slots=True)
class GuessMessage:
    type: Literal["guess"]
    value: str


@dataclass(slots=True)
class LeaveMessage:
    type: Literal["leave"]


@dataclass(slots=True)
class GameStateMessage:
    type: Literal["game_state"]
    code: str
    status: str
    players: list[dict] = field(default_factory=list)
    round: int = 0


@dataclass(slots=True)
class ErrorMessage:
    type: Literal["error"]
    message: str
    code: str | None = None
