from __future__ import annotations

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings
from backend.db.models import Base, CompletedGame

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialise_database() -> None:
    Base.metadata.create_all(bind=engine)


def save_completed_game(code: str, language_a: str, language_b: str, winner_name: str | None, target_word_a: str | None, target_word_b: str | None) -> CompletedGame:
    with SessionLocal() as session:
        record = CompletedGame(
            code=code,
            language_a=language_a,
            language_b=language_b,
            winner_name=winner_name,
            target_word_a=target_word_a,
            target_word_b=target_word_b,
            finished_at=datetime.utcnow(),
            summary=f"winner={winner_name}",
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
