"""
SQLAlchemy setup. Connects to the Supabase Postgres instance via
DATABASE_URL (found in Supabase Dashboard -> Project Settings ->
Database -> Connection string -> URI, "Session pooler" recommended).

Falls back to a local SQLite file if DATABASE_URL isn't set, so the
app (and the test suite) can still run without a live Supabase project.

Tables are created automatically on startup via `init_db()`, called
from main.py's startup event — no manual migration step needed for
this capstone-scale project.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

_DB_URL = settings.DATABASE_URL or "sqlite:///./careerpilot_dev.db"

_connect_args = {"check_same_thread": False} if _DB_URL.startswith("sqlite") else {}

engine = create_engine(_DB_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    # Import models here so they're registered on Base before create_all runs.
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
