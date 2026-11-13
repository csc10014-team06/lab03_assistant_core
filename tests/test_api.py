"""Integration tests for Assistant Web API — Scaffold & Fixtures (han_htg)."""

from __future__ import annotations

import dataclasses

import httpx
import pytest
from starlette.testclient import TestClient

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.config import Settings
from assistant_core.data_loader import load_handbook, load_offices
from assistant_core.llm import FakeLLM
from assistant_core.service import AssistantService

OK_JSON = {
    "current": {
        "time": "2026-10-05T09:00",
        "temperature_2m": 31.2,
        "weather_code": 3,
        "wind_speed_10m": 8.5,
    }
}


def weather_with(handler) -> WeatherClient:
    transport = httpx.MockTransport(handler)
    return WeatherClient("https://example.test/forecast", 10.76, 106.68, retries=1, transport=transport)


@pytest.fixture
def settings():
    # In-memory database: tests never touch the real assistant.db.
    return Settings(db_url="sqlite://", hash_salt="test-salt-123")


@pytest.fixture
def service(settings):
    return AssistantService(
        settings,
        load_offices(settings.offices_path),
        load_handbook(settings.handbook_path),
        FakeLLM(),
    )


@pytest.fixture
def repo(settings):
    engine = make_engine(settings.db_url)
    init_db(engine)
    return Repository(engine, settings.require_hash_salt())


@pytest.fixture
def client(settings, service, repo):
    settings = dataclasses.replace(settings, api_admin_key="secret-admin", rate_limit_per_min=5)
    app = create_app(settings, service, weather_with(lambda req: httpx.Response(200, json=OK_JSON)), repo)
    return TestClient(app)


# --- Health check (han_htg) ---
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


# --- T1 chat (vy_th) ---
def test_chat_fee(client):
    r = client.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"})
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "fee" and "9,450,000" in body["answer"] and body["request_id"]


def test_chat_validation_error(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_rate_limit(client):
    codes = [client.post("/v1/chat", json={"message": "hi"}).status_code for _ in range(6)]
    assert codes[-1] == 429


# --- T2/T3 feedback (dieu_sp) ---
def test_feedback_roundtrip(client, repo):
    # shortcut: /v1/chat does not record interactions yet (vy_th's task); use its request_id once it does
    repo.record_interaction("s1", "abc123", "fee", None, True, False, 1.0)
    r = client.post("/v1/feedback", json={"request_id": "abc123", "rating": 1})
    assert r.status_code == 201 and r.json()["id"] == 1
    assert client.get("/v1/feedback").status_code == 401
    listed = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"})
    assert listed.status_code == 200 and len(listed.json()) == 1


def test_feedback_unknown_request_id_returns_404(client):
    r = client.post("/v1/feedback", json={"request_id": "nope", "rating": 1})
    assert r.status_code == 404
    assert r.json() == {"error": {"code": "unknown_request_id", "message": "Unknown request id"}}


def test_feedback_list_newest_first(client, repo):
    for rid in ("r1", "r2", "r3"):
        repo.record_interaction("s1", rid, "fee", None, True, False, 1.0)
        assert client.post("/v1/feedback", json={"request_id": rid, "rating": 1}).status_code == 201
    listed = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"}).json()
    assert [f["request_id"] for f in listed] == ["r3", "r2", "r1"]


@pytest.mark.parametrize("limit", [0, -1, 101])
def test_feedback_list_limit_out_of_range(client, limit):
    r = client.get("/v1/feedback", params={"limit": limit}, headers={"X-API-Key": "secret-admin"})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_feedback_rating_out_of_range(client):
    assert client.post("/v1/feedback", json={"request_id": "x", "rating": 5}).status_code == 422


# --- T4 weather (nhat_npm) ---
def test_weather_ok(client):
    r = client.get("/v1/weather")
    assert r.status_code == 200
    assert r.json() == {
        "temperature_c": 31.2,
        "wind_kmh": 8.5,
        "description": "overcast",
        "observed_at": "2026-10-05T09:00",
        "stale": False,
    }


def test_weather_down_returns_503(settings, service):
    def upstream_down(_request):
        return httpx.Response(503)

    weather = weather_with(upstream_down)
    app = create_app(settings, service, weather)
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503
    assert r.json() == {
        "error": {
            "code": "weather_service_unavailable",
            "message": "Weather service unavailable",
        }
    }


def test_weather_stale_cache_when_upstream_fails(settings, service):
    responses = iter([httpx.Response(200, json=OK_JSON), httpx.Response(503), httpx.Response(503)])
    weather = WeatherClient(
        "https://example.test/forecast",
        10.76,
        106.68,
        retries=1,
        cache_ttl_s=0,
        transport=httpx.MockTransport(lambda _request: next(responses)),
    )
    client = TestClient(create_app(settings, service, weather))

    first = client.get("/v1/weather")
    stale = client.get("/v1/weather")

    assert first.status_code == 200 and first.json()["stale"] is False
    assert stale.status_code == 200 and stale.json()["stale"] is True
    assert stale.json()["temperature_c"] == 31.2


# --- H1 offices (truyen_lp) ---
def test_offices_ok(client):
    r = client.get("/v1/offices")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    names = [item["name"] for item in data]
    assert names == sorted(names)
    assert names == ["IT Helpdesk", "Library", "Student Affairs", "Training Office"]


def test_offices_contains_library(client):
    r = client.get("/v1/offices")
    assert r.status_code == 200
    data = r.json()
    library = next((item for item in data if item["name"] == "Library"), None)
    assert library is not None
    assert library["room"] == "B.201"
    assert "Mon-Sat" in library["hours"]
