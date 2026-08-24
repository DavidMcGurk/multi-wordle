from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Language(str, Enum):
    EN = "en"
    HU = "hu"


class GameStatus(str, Enum):
    CREATE = "CREATE"
    WAITING_FOR_OPPONENT = "WAITING_FOR_OPPONENT"
    READY = "READY"
    COUNTDOWN = "COUNTDOWN"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


@dataclass(slots=True)
class Player:
    id: str
    session_token: str
    name: str
    language: Language | None = None
    ready: bool = False
    is_connected: bool = True
    guesses: list[str] = field(default_factory=list)
    total_guesses: int = 0
    best_progress: list[int] = field(default_factory=list)
    won: bool = False
    outcome: str | None = None
    resolved_at: float | None = None


@dataclass(slots=True)
class Game:
    code: str
    players: list[Player]
    status: GameStatus = GameStatus.CREATE
    target_words: dict[str, str] = field(default_factory=dict)
    winner_id: str | None = None
    winner_decided_at: float | None = None
    created_at: float = 0.0
    updated_at: float = 0.0
    started_at: float | None = None
    ended_at: float | None = None
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
