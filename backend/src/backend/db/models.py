from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CompletedGame(Base):
    __tablename__ = "completed_games"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    winner_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language_a: Mapped[str] = mapped_column(String(2), nullable=False)
    language_b: Mapped[str] = mapped_column(String(2), nullable=False)
    target_word_a: Mapped[str | None] = mapped_column(String(16), nullable=True)
    target_word_b: Mapped[str | None] = mapped_column(String(16), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
