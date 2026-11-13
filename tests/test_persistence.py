"""tests/test_persistence.py — Verification of persistence in SQLite database.

Owner: nhat_dm
Task: Lab 5 Persistence tests (Issue #34, tutorial §E.6)
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.main import create_app
from assistant_core.config import Settings
from assistant_core.data_loader import load_handbook, load_offices
from assistant_core.llm import FakeLLM
from assistant_core.service import AssistantService


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Provide an isolated SQLite file path in a temporary directory."""
    return tmp_path / "test_persistence.db"


@pytest.fixture
def salt() -> str:
    return "test-persistence-salt"


@pytest.fixture
def admin_key() -> str:
    return "test-admin-secret"


@pytest.fixture
def app_factory(db_path: Path, salt: str, admin_key: str) -> Callable[[], TestClient]:
    """Factory creating a new FastAPI TestClient attached to the persistent SQLite file."""

    def _create() -> TestClient:
        settings = Settings(
            db_url=f"sqlite:///{db_path}",
            hash_salt=salt,
            api_admin_key=admin_key,
        )
        service = AssistantService(
            settings,
            load_offices(settings.offices_path),
            load_handbook(settings.handbook_path),
            FakeLLM(),
        )
        engine = make_engine(settings.db_url)
        init_db(engine)
        repo = Repository(engine, settings.require_hash_salt())
        app = create_app(settings=settings, service=service, repo=repo)
        return TestClient(app)

    return _create


def test_fixture_app_factory_creates_client(app_factory: Callable[[], TestClient]):
    client = app_factory()
    r = client.get("/health")
    assert r.status_code == 200
