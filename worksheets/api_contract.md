# Lab 4 — API contract worksheet

Fill in one row per endpoint **before** you code it.

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | /health | — | 200 {status, version} | — | ops, UI |
| POST | /v1/chat | | | | UI, tests |
| POST | /v1/feedback | JSON `{request_id: str 1–64, rating: int -1..1, comment?: str ≤500}` | 201 `{request_id, rating, comment, id, created_at}` | 422 `invalid_request` (missing field, rating out of range, comment too long) | UI (thumbs up / neutral / down after an answer) |
| GET | /v1/feedback | header X-API-Key | 200 list of `{request_id, rating, comment, id, created_at}` (oldest first) | 401 `missing_or_invalid_api_key` when the key is absent or wrong | staff dashboard |
| GET | /v1/weather | — | 200 `{temperature_c, wind_kmh, description, observed_at, stale}`; `stale: true` means cached weather | 503 `weather_service_unavailable` when there is no usable cached result | UI shows current or last cached weather; otherwise “Weather service unavailable” |

Questions:
1. Which fields are required, and what are their limits?
2. What does the UI show for each error code?
3. What changes would force a `/v2`?

