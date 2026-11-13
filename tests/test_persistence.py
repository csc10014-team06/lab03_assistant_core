"""tests/test_persistence.py — Verification of persistence in SQLite database.

Owner: nhat_dm
Task: Lab 5 Persistence tests (Issue #34, tutorial §E.6)
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from sqlmodel import Session, select
from starlette.testclient import TestClient

from assistant_api.db import ChatSession, Feedback, Interaction, Repository, hash_session, init_db, make_engine
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


def test_session_hashing_stability_and_salt_dependence(
    app_factory: Callable[[], TestClient], db_path: Path, salt: str
):
    """Session IDs are hashed deterministically with salt; same session maps to one row."""
    # 1. Direct unit verification of the hash_session function
    h1 = hash_session("student_session_1", salt)
    h2 = hash_session("student_session_1", salt)
    h_diff_sess = hash_session("student_session_2", salt)
    h_diff_salt = hash_session("student_session_1", "different-salt-999")

    assert len(h1) == 16
    assert h1 == h2  # Stable & deterministic
    assert h1 != h_diff_sess  # Distinct for different sessions
    assert h1 != h_diff_salt  # Changes when salt changes

    # 2. Database level: 3 chats in same session should produce only 1 ChatSession row
    client = app_factory()
    for msg in ("hi", "where is the library?", "fees for 10 credits"):
        r = client.post("/v1/chat", json={"message": msg, "session_id": "student_session_1"})
        assert r.status_code == 200

    # 1 chat with a second session
    r2 = client.post("/v1/chat", json={"message": "hi", "session_id": "student_session_2"})
    assert r2.status_code == 200

    engine = make_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        sessions = session.exec(select(ChatSession)).all()
        interactions = session.exec(select(Interaction)).all()

        # Exactly 2 unique chat sessions recorded
        assert len(sessions) == 2
        assert {s.id for s in sessions} == {h1, h_diff_sess}

        # 4 total interactions, 3 pointing to session 1, 1 pointing to session 2
        assert len(interactions) == 4
        s1_interactions = [i for i in interactions if i.session_id == h1]
        s2_interactions = [i for i in interactions if i.session_id == h_diff_sess]
        assert len(s1_interactions) == 3
        assert len(s2_interactions) == 1


def test_raw_session_id_and_message_text_not_stored_in_db(
    app_factory: Callable[[], TestClient], db_path: Path
):
    """Privacy requirement: raw session IDs and message text are never persisted to SQLite."""
    raw_session = "my_top_secret_raw_session_string_xyz"
    raw_message = "confidential_personal_inquiry_for_credits"

    client = app_factory()
    resp = client.post("/v1/chat", json={"message": raw_message, "session_id": raw_session})
    assert resp.status_code == 200

    # Scan the raw SQLite database content across all tables and columns
    con = sqlite3.connect(db_path)
    try:
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        all_text_values: list[str] = []
        for table in tables:
            rows = con.execute(f"SELECT * FROM {table}").fetchall()  # noqa: S608 — test inspection
            for row in rows:
                for val in row:
                    if isinstance(val, str):
                        all_text_values.append(val)

        # Neither the raw session string nor the message text should appear anywhere in the database
        assert not any(raw_session in text for text in all_text_values)
        assert not any(raw_message in text for text in all_text_values)
    finally:
        con.close()


def test_migration_is_idempotent_when_run_twice(tmp_path: Path):
    """Running scripts/migrate.py twice on the same DB file succeeds safely without errors."""
    db_file = tmp_path / "migrated.db"
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "migrate.py"
    assert script_path.exists()

    # First migration run: creates tables and applies all migration files
    run1 = subprocess.run(
        [sys.executable, str(script_path), str(db_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run1.returncode == 0
    assert "apply" in run1.stdout

    # Second migration run: should detect existing schema and skip already applied scripts
    run2 = subprocess.run(
        [sys.executable, str(script_path), str(db_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run2.returncode == 0
    assert "skip" in run2.stdout

    # Check database integrity: verify essential tables exist
    con = sqlite3.connect(db_file)
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "schema_version" in tables
        assert "chat_session" in tables
        assert "interaction" in tables
        assert "feedback" in tables
    finally:
        con.close()


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
