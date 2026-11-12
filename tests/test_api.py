"""Integration tests for Assistant Web API — Scaffold & Fixtures (han_htg)."""

from __future__ import annotations

import dataclasses

import httpx
import pytest
from starlette.testclient import TestClient

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
    return Settings()


@pytest.fixture
def service(settings):
    return AssistantService(
        settings,
        load_offices(settings.offices_path),
        load_handbook(settings.handbook_path),
        FakeLLM(),
    )


@pytest.fixture
def client(settings, service):
    settings = dataclasses.replace(settings, api_admin_key="secret-admin", rate_limit_per_min=5)
    app = create_app(settings, service, weather_with(lambda req: httpx.Response(200, json=OK_JSON)))
    return TestClient(app)


# --- Health check (han_htg) ---
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


# --- T1 chat (vy_th) ---
# vy_th will paste: test_chat_fee, test_chat_validation_error, test_rate_limit


# --- T2/T3 feedback (dieu_sp) ---
def test_feedback_roundtrip(client):
    r = client.post("/v1/feedback", json={"request_id": "abc123", "rating": 1})
    assert r.status_code == 201 and r.json()["id"] == 1
    assert client.get("/v1/feedback").status_code == 401
    listed = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"})
    assert listed.status_code == 200 and len(listed.json()) == 1


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
