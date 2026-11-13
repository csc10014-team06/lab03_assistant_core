"""FastAPI web application exposing the study assistant core over HTTP.

Endpoints (v1): GET /health, POST /v1/chat, POST /v1/feedback, GET /v1/feedback, GET /v1/weather
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.ratelimit import RateLimiter
from assistant_api.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    FeedbackIn,
    FeedbackOut,
    OfficeOut,
    Weather,
)
from assistant_api.weather import ExternalServiceError, WeatherClient
from assistant_core.cli import build_service
from assistant_core.config import Settings, load_settings
from assistant_core.models import Message
from assistant_core.service import AssistantService


def create_app(
    settings: Settings | None = None,
    service: AssistantService | None = None,
    weather: WeatherClient | None = None,
    repo: Repository | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    service = service or build_service(settings)
    weather = weather or WeatherClient(
        settings.weather_url, settings.campus_lat, settings.campus_lon, timeout_s=settings.weather_timeout_s
    )
    limiter = RateLimiter(settings.rate_limit_per_min)  # noqa: F841 — used in BONUS task
    if repo is None:
        engine = make_engine(settings.db_url)
        init_db(engine)
        repo = Repository(engine, settings.require_hash_salt())

    app = FastAPI(
        title="Study Assistant API", version="1.0.0", description="Backend of the CSC10014 Smart Virtual Assistant."
    )

    @app.exception_handler(RequestValidationError)
    def handle_validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]
        field = first["loc"][-1]
        msg = first["msg"]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "validation_error", "message": f"{field}: {msg}"}},
        )

    def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
        if not settings.api_admin_key or x_admin_key != settings.api_admin_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key")

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/v1/chat",
        response_model=ChatResponse,
        tags=["chat"],
        responses={429: {"model": ErrorResponse}},
    )
    def chat(req: ChatRequest) -> ChatResponse:
        if not limiter.allow(req.session_id):
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests",
            )

        start = time.perf_counter()

        resp = service.respond(
            Message(text=req.message, session_id=req.session_id)
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        request_id = uuid.uuid4().hex[:12]

        topic = (
            resp.sources[0].id
            if resp.intent.value == "rule" and resp.sources
            else None
        )

        repo.record_interaction(
            raw_session=req.session_id,
            request_id=request_id,
            intent=resp.intent.value,
            topic=topic,
            resolved=resp.intent.value != "unknown",
            degraded=resp.degraded,
            latency_ms=elapsed_ms,
        )

        return ChatResponse(
            **resp.model_dump(),
            request_id=request_id,
        )

    @app.post(
        "/v1/feedback",
        response_model=FeedbackOut,
        status_code=201,
        tags=["feedback"],
        responses={404: {"model": ErrorResponse}},
    )
    def add_feedback(fb: FeedbackIn) -> FeedbackOut:
        saved = repo.add_feedback(fb.request_id, fb.rating, fb.comment)
        if saved is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown request id")
        return FeedbackOut.model_validate(saved, from_attributes=True)

    @app.get("/v1/feedback", response_model=list[FeedbackOut], tags=["feedback"], dependencies=[Depends(require_admin)])
    def list_feedback(limit: int = Query(100, ge=1, le=100)) -> list[FeedbackOut]:
        # The API-key check is already done by `require_admin` above.
        return [FeedbackOut.model_validate(f, from_attributes=True) for f in repo.list_feedback(limit)]

    @app.get("/v1/weather", response_model=Weather, tags=["external"], responses={503: {"model": ErrorResponse}})
    def campus_weather() -> Weather:
        try:
            return weather.current()
        except ExternalServiceError as err:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=err.message) from err

    @app.get("/v1/offices", response_model=list[OfficeOut], tags=["offices"])
    def list_offices() -> list[OfficeOut]:
        return [OfficeOut(**asdict(o)) for o in service.offices()]

    return app
