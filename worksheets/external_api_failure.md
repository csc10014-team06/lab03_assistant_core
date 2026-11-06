# Lab 4 homework — design for an external service that goes down

Service chosen: Open-Meteo campus weather
Base URL: `https://api.open-meteo.com/v1/forecast`

The `WeatherClient` uses a 3-second HTTP timeout, retries once after a failed
attempt, and caches a successful result for 600 seconds. If an upstream call
fails after retries, it returns stale cached weather when available; otherwise
it raises `ExternalServiceError`. The API returns the weather result (with
`stale: true` for fallback data) or maps that exception to HTTP 503.

| Failure | How you simulate it | What your API returns | What the user sees |
|---|---|---|---|
| Timeout | `httpx.MockTransport` handler raises `httpx.ConnectTimeout` | Cached weather with `stale: true`, or HTTP 503 with `weather_service_unavailable` when there is no cached result | The last available weather, or “Weather service unavailable” |
| 500 from upstream | Mock transport returns `httpx.Response(500)` | Cached weather with `stale: true`, or HTTP 503 with `weather_service_unavailable` | The last available weather, or “Weather service unavailable” |
| Malformed JSON | Mock transport returns HTTP 200 with `{}`; the expected `current` object is missing | Cached weather with `stale: true`, or HTTP 503 with `weather_service_unavailable` | The last available weather, or “Weather service unavailable” |
| Rate limited (429) | Mock transport returns `httpx.Response(429)` | Cached weather with `stale: true`, or HTTP 503 with `weather_service_unavailable` | The last available weather, or “Weather service unavailable” |

Timeout value and why: 3 seconds, as specified for the provided client, to
bound waiting for the external site.
Retries and why: one retry after the initial attempt, as configured by the
provided client.
Cache TTL and why: 600 seconds, the provided client default; this allows
recent weather to be served during a short upstream outage.

Tests added (`tests/test_api.py`): `test_weather_ok`,
`test_weather_down_returns_503`, and
`test_weather_stale_cache_when_upstream_fails`.
