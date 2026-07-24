"""Moteur SQLAlchemy + session. SQLite en dev, PostgreSQL en prod."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Crée les tables si elles n'existent pas (idempotent)."""
    from app import models  # noqa: F401 — enregistre les modèles

    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """Dépendance FastAPI : ouvre/ferme une session par requête."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
