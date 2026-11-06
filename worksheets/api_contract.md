# Lab 4 — API contract worksheet

Fill in one row per endpoint **before** you code it.

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | /health | — | 200 {status, version} | — | ops, UI |
| POST | /v1/chat | JSON: message (required, 1–2000 chars), session_id (optional, max 64 chars) | 200 {answer, intent, sources, degraded, request_id} | 422 invalid_request; 429 too_many_requests | UI, tests |
| 
| POST | /v1/feedback | | | | UI |
| GET | /v1/feedback | header X-API-Key | | | staff dashboard |
| GET | /v1/weather | — | 200 `{temperature_c, wind_kmh, description, observed_at, stale}`; `stale: true` means cached weather | 503 `weather_service_unavailable` when there is no usable cached result | UI shows current or last cached weather; otherwise “Weather service unavailable” |

Questions:
1. Which fields are required, and what are their limits?
2. What does the UI show for each error code?
3. What changes would force a `/v2`?

