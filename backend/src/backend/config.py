from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "wordle-race"
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/wordle")
    game_ttl_seconds: int = int(os.getenv("GAME_TTL_SECONDS", "1800"))
    max_players_per_game: int = 2
    max_guesses_per_game: int = 6
    join_code_length: int = 5

settings = Settings()
