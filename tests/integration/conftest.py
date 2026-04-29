"""Integration-test fixtures.

Requirements:
- DATABASE_URL pointing at a Postgres + pgvector test database (e.g.
  postgresql+psycopg://elon:elon@localhost:5432/elon_test).

Each test module gets a fresh schema via Base.metadata.create_all/drop_all.
External dependencies (Anthropic, Telegram, MinIO) are monkey-patched.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="module")
def engine():
    if not os.getenv("DATABASE_URL"):
        pytest.skip("no DATABASE_URL")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    from sqlalchemy import create_engine
    from elon.core.models import Base

    db_url = os.getenv("DATABASE_URL")
    eng = create_engine(db_url, future=True)
    with eng.connect() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def app_client(engine, monkeypatch):
    from fastapi.testclient import TestClient
    # Rebind SessionLocal to the test engine BEFORE importing the app.
    from sqlalchemy.orm import sessionmaker

    import elon.core.db as core_db
    core_db.engine = engine
    core_db.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    # Stub out external side-effects so endpoints don't try to talk to the world.
    monkeypatch.setattr("elon.chat.notify.send_telegram", lambda *a, **k: {"ok": True})

    from elon.api.main import app
    return TestClient(app)
