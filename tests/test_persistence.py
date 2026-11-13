"""tests/test_persistence.py — Verification of persistence in SQLite database.

Owner: nhat_dm
Task: Lab 5 Persistence tests (Issue #34, tutorial §E.6)
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from sqlmodel import Session, select
from starlette.testclient import TestClient

from assistant_api.db import Feedback, Repository, init_db, make_engine
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


def test_feedback_survives_restart(app_factory: Callable[[], TestClient], admin_key: str):
    """Grading requirement: feedback saved in SQLite survives restarting the app.

    Workflow:
    1. Instance A handles a chat and records an interaction in SQLite.
    2. Instance A accepts feedback for that interaction.
    3. Simulate shutdown and restart: Instance B boots against the identical SQLite file.
    4. Query feedback via admin endpoint on Instance B: the feedback record is fully preserved.
    """
    client_a = app_factory()

    # 1. Chat to create an interaction
    chat_resp = client_a.post("/v1/chat", json={"message": "where is the library?", "session_id": "sess-restart-1"})
    assert chat_resp.status_code == 200
    req_id = chat_resp.json()["request_id"]
    assert req_id

    # 2. Submit feedback
    fb_resp = client_a.post(
        "/v1/feedback",
        json={"request_id": req_id, "rating": 1, "comment": "very helpful answer"},
    )
    assert fb_resp.status_code == 201
    feedback_id = fb_resp.json()["id"]

    # 3. Simulate process termination and restart with a completely new app/client instance
    del client_a
    client_b = app_factory()

    # 4. Verify feedback persists across process boundary
    list_resp = client_b.get("/v1/feedback", headers={"X-API-Key": admin_key})
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["id"] == feedback_id
    assert items[0]["request_id"] == req_id
    assert items[0]["rating"] == 1
    assert items[0]["comment"] == "very helpful answer"


def test_feedback_unknown_request_id_returns_404_and_writes_nothing(
    app_factory: Callable[[], TestClient], db_path: Path
):
    """Submitting feedback for an unrecorded request_id returns 404 and writes zero rows."""
    client = app_factory()

    # Attempt feedback on a non-existent request id
    resp = client.post(
        "/v1/feedback",
        json={"request_id": "ghost-request-id", "rating": -1, "comment": "should not exist"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_request_id"

    # Verify directly against SQLite that no phantom feedback row was written
    engine = make_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        feedbacks = session.exec(select(Feedback)).all()
        assert len(feedbacks) == 0


def test_feedback_multiple_submissions_allowed_for_same_request_id(
    app_factory: Callable[[], TestClient], admin_key: str
):
    """Documenting agreed behavior with dieu_sp for duplicate feedback requests.

    In the current schema (Feedback.request_id indexed with non-unique foreign key),
    submitting multiple feedback entries for the same interaction is permitted
    (e.g., student updates their review or adds further comments).
    Each submission creates an independent feedback record with a distinct auto-incremented id.
    """
    client = app_factory()

    # Create interaction
    chat_resp = client.post("/v1/chat", json={"message": "fees for 10 credits", "session_id": "sess-dup-1"})
    assert chat_resp.status_code == 200
    req_id = chat_resp.json()["request_id"]

    # Submit first feedback
    fb1 = client.post("/v1/feedback", json={"request_id": req_id, "rating": 0, "comment": "initial neutral reaction"})
    assert fb1.status_code == 201
    id1 = fb1.json()["id"]

    # Submit second feedback on the same request_id
    fb2 = client.post("/v1/feedback", json={"request_id": req_id, "rating": 1, "comment": "updated positive review"})
    assert fb2.status_code == 201
    id2 = fb2.json()["id"]

    assert id1 != id2

    # Verify both records are retrieved via admin endpoint in newest-first order
    list_resp = client.get("/v1/feedback", headers={"X-API-Key": admin_key})
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 2
    assert [item["id"] for item in items] == [id2, id1]
    assert [item["comment"] for item in items] == ["updated positive review", "initial neutral reaction"]
