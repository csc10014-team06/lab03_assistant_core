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
def test_chat_fee(client):
    response = client.post(
        "/v1/chat",
        json={"message": "tuition for 18 credits and 2 retake"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Your tuition is 9,450,000 VND."
    assert data["intent"] == "fee"
    assert data["sources"] == []
    assert data["degraded"] is False
    assert len(data["request_id"]) == 12


def test_chat_validation_error(client):
    response = client.post(
        "/v1/chat",
        json={"message": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_rate_limit(client):
    for _ in range(5):
        response = client.post(
            "/v1/chat",
            json={"message": "hello"},
        )
        assert response.status_code == 200

    response = client.post(
        "/v1/chat",
        json={"message": "hello"},
    )
    assert response.status_code == 429


# --- T2/T3 feedback (dieu_sp) ---
# dieu_sp will paste: test_feedback_roundtrip, test_feedback_rating_out_of_range


# --- T4 weather (nhat_npm) ---
# nhat_npm will paste: test_weather_ok, test_weather_down_returns_503, test_weather_stale_cache_when_upstream_fails


# --- H1 offices (truyen_lp) ---
# truyen_lp will paste: test_offices_ok, test_offices_contains_library
