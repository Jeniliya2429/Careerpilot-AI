"""
Shared pytest fixtures. Forces a throwaway SQLite DB and dummy secrets
so the full test suite runs with zero network calls and zero real
credentials — safe to run in CI or offline.
"""
import os
import sys

# Must be set BEFORE any `app.*` module is imported, since app.config
# reads env vars at import time.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_careerpilot.db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy-key-not-real")
os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-dummy-key")
os.environ.setdefault("CHROMA_PERSIST_DIR", "./test_chroma_db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models  # noqa: F401 registers models on Base

TEST_DB_URL = "sqlite:///./test_careerpilot.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Registers a fresh user and returns Authorization headers for it."""
    resp = client.post("/auth/register", json={
        "name": "Test User", "email": "test@example.com", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
