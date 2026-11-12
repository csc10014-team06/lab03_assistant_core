# Lab 4 — Team plan: the assistant as a web API (7 members)

Goal: expose our Lab 3 `assistant_core` over HTTP with FastAPI — the 5 endpoints of
tutorial §D.2, homework H1 (`GET /v1/offices`) and rate limiting (Part F) — with all
tests of tutorial Part E green, **without changing any Week 3 test**.

Source of the starter files: `public_materials` → `lab04/starter/`.

## 0. What we copy from the starter — and what we don't

The starter ships its *own* `assistant_core` (a reference solution). Its API code is written
against that version, which is **not** compatible with ours:

| Starter's `assistant_api` expects | Our Lab 3 `assistant_core` has |
|---|---|
| `service.handle(Message) -> Response` (answer, intent, sources, degraded) | `handle(str) -> str` |
| fee answer `"Your tuition is 9,450,000 VND."` | `"Your tuition is 9450000 VND"` — pinned by `test_characterization.py`, `test_service.py`, `test_cli.py` |
| pydantic `Settings` with `api_admin_key`, `weather_url`, … and `.model_copy()` | frozen dataclass `Settings` without those fields |
| `service.offices.all()` (H1) | offices are a `dict[str, Office]` inside the service |

So: **do not copy `starter/src/assistant_core/`, `starter/data/`, or the starter's
`test_service.py` / `test_router.py` / `test_tools.py`** (they test the reference package, not ours;
our data files are byte-identical already). We *add* a small bridge to our package instead.

| Starter file | Action | Goes to |
|---|---|---|
| `src/assistant_api/__init__.py`, `ratelimit.py`, `weather.py` | copy as-is | `assistant_api/` |
| `src/assistant_api/schemas.py` | copy; import `Intent`, `Source` from **our** `assistant_core.models` | `assistant_api/schemas.py` |
| `src/assistant_api/main.py` | copy; change imports + `build_service` call (see §2) | `assistant_api/main.py` |
| `tests/test_api.py` | copy; **test bodies unchanged**, fixtures adapted (see §2) | `tests/test_api.py` |
| `api-tests/curl_tests.sh`, `api-tests/*.postman_collection.json` | copy as-is | `api-tests/` |
| `requirements.txt`, `pyproject.toml` deps | merge `fastapi`, `httpx`, `uvicorn` into ours | root |
| `.env.example` | merge the "Lab 4 — API" block, using our `ASSISTANT_` prefix | root |
| `lab04/worksheets/*.md` | copy | `worksheets/` |
| `lab04/practice/` | **individual warm-up** (P1–P5) — do it on your own machine, do not merge into `main` | — |

Note: the starter uses a `src/` layout; we keep our flat layout, so `assistant_api/` sits next to
`assistant_core/`.

## 1. Target layout (new/changed files only)

```
assistant_core/
  models.py          # NEW  nhat_dm   Intent, Message, Source, Response (pydantic)
  service.py         # +    nhat_dm   respond(Message) -> Response; offices() for H1
  offices.py         # +    truyen_lp all_offices(...) sorted by name (H1)
  config.py          # +    long_th   API settings fields + env vars
assistant_api/       # NEW  han_htg   package scaffold copied from starter
  __init__.py, main.py, schemas.py, weather.py, ratelimit.py
tests/
  test_api.py        # NEW  han_htg (fixtures) + each endpoint owner adds the prof's tests
  test_models.py     # NEW  nhat_dm   tests for respond()
  test_config_api.py # NEW  long_th   tests for the new settings
api-tests/           # NEW  han_htg   curl script + Postman collection
worksheets/api_contract.md, worksheets/external_api_failure.md   # NEW
pyproject.toml, requirements.txt, .env.example, README.md, .github/workflows/ci.yml   # updated
```

**Rule:** existing files under `tests/` are frozen. New tests go into new files
(or into `tests/test_api.py`, which is new this week).

## 2. Interface contracts (agree on these FIRST — day 1)

```python
# assistant_core/models.py            (nhat_dm) — same shape as the starter's models.py
class Intent(str, Enum): GREETING="greeting"; FEE="fee"; OFFICE="office"; RULE="rule"; UNKNOWN="unknown"
class Message(BaseModel):  text: str = Field(min_length=1, max_length=2000); session_id: str = "local"
class Source(BaseModel):   id: str; title: str
class Response(BaseModel): answer: str; intent: Intent; sources: list[Source] = []; degraded: bool = False

# assistant_core/service.py           (nhat_dm)
class AssistantService:
    def handle(self, message: str) -> str: ...        # UNCHANGED — CLI + Week 3 tests
    def respond(self, msg: Message) -> Response: ...  # NEW — used by the API
    def offices(self) -> list[Office]: ...            # NEW — delegates to offices.all_offices (H1)

# assistant_core/offices.py           (truyen_lp)
def all_offices(offices: dict[str, Office]) -> list[Office]: ...   # sorted by name

# assistant_core/config.py            (long_th) — new Settings fields, all with defaults
api_admin_key: str | None = field(default=None, repr=False)   # ASSISTANT_API_ADMIN_KEY
weather_url: str = "https://api.open-meteo.com/v1/forecast"   # ASSISTANT_WEATHER_URL
weather_timeout_s: float = 3.0                                # ASSISTANT_WEATHER_TIMEOUT_S
campus_lat: float = 10.7626                                   # ASSISTANT_CAMPUS_LAT
campus_lon: float = 106.6822                                  # ASSISTANT_CAMPUS_LON
rate_limit_per_min: int = 30                                  # ASSISTANT_RATE_LIMIT_PER_MIN

# assistant_api/main.py               (han_htg) — signature kept from the starter
def create_app(settings: Settings | None = None,
               service: AssistantService | None = None,
               weather: WeatherClient | None = None) -> FastAPI: ...
#   service defaults to assistant_core.cli.build_service(settings)
#   T1 calls service.respond(Message(...)) instead of service.handle(...)
```

`respond()` rules (nhat_dm):
- Same routing as `handle()` (reuse the existing private helpers — no duplicated keyword logic).
- Fee answer formatted with thousands separators: `f"Your tuition is {total:,} VND."` → `test_api.py`
  checks for `"9,450,000"`. `handle()` keeps the old format so Week 3 tests stay green.
- Rule answers: `answer` without the `(source: …)` suffix; the rule goes into `sources`.
  On `LLMError` fall back to the rule text and set `degraded=True`.
- **Do not expose CLI commands over HTTP**: `history`, `stats`, `save …` must *not* be executed by
  `respond()` (otherwise any web client could read other users' history or write files on the
  server). Treat them as normal text.

`tests/test_api.py` fixture adaptation (han_htg) — the prof's test **functions stay verbatim**;
only the fixtures change because our `Settings` is a dataclass and our service is built differently:

```python
@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def service(settings):
    return AssistantService(settings, load_offices(settings.offices_path),
                            load_handbook(settings.handbook_path), FakeLLM())

@pytest.fixture
def client(settings, service):
    settings = dataclasses.replace(settings, api_admin_key="secret-admin", rate_limit_per_min=5)
    app = create_app(settings, service, weather_with(lambda req: httpx.Response(200, json=OK_JSON)))
    return TestClient(app)
```

## 3. Assignments

| Owner | Work item | Main tasks | Done when |
|---|---|---|---|
| **long_th** (lead) | config + packaging + integration | Add the 6 API fields to `Settings` + `load_settings()`; merge deps (`fastapi==0.115.0`, `httpx==0.27.2`, `uvicorn==0.30.6`) into `pyproject.toml` and `requirements.txt`; add `assistant_api*` to `[tool.setuptools.packages.find] include`; bump version to `0.4.0`; extend `.env.example`. New tests in `tests/test_config_api.py`. Merges PRs in the order of §4 and tags **`v0.4-api`**. | `ruff check` + `pytest` green on `main`; admin key never in `repr()` |
| **nhat_dm** | service bridge | `assistant_core/models.py` + `AssistantService.respond()` + `AssistantService.offices()` per §2. Tests in `tests/test_models.py`: fee (with commas), office, rule with source, LLM failure → `degraded=True`, `"save x"` does **not** write a file. | All Week 3 tests still green; new tests green |
| **han_htg** | API scaffold + docs | Copy `assistant_api/` per §0 with T1–T4 still `raise NotImplementedError` (so others only fill in function bodies); `/health` working; `tests/test_api.py` with adapted fixtures + `test_health` + empty section headers (`# --- T1 chat (vy_th) ---` etc.) so each owner pastes into their own section; `api-tests/`; README "Run the API" section; CI unchanged except deps. | `uvicorn assistant_api.main:create_app --factory --reload` starts; `/docs` shows the endpoints |
| **vy_th** | **T1** `POST /v1/chat` + **Part F** rate limiting | Implement chat with `service.respond(...)` + `request_id`; add the rate-limit check at the top of `chat()`; paste `test_chat_fee`, `test_chat_validation_error`, `test_rate_limit` (**remove** the `@pytest.mark.skip` line). Take the `/docs` screenshot of a successful `/v1/chat` for the PR. | 3 tests green; 6th request in a minute → 429 |
| **dieu_sp** | **T2** `POST /v1/feedback` + **T3** `GET /v1/feedback` | Implement both (in-memory `feedback_store`); paste `test_feedback_roundtrip`, `test_feedback_rating_out_of_range`; fill the feedback rows of `worksheets/api_contract.md`. | 201 / 401 / 200 / 422 behave as in §D.2 |
| **nhat_npm** | **T4** `GET /v1/weather` | Implement the `try/except ExternalServiceError → 503`; paste `test_weather_ok`, `test_weather_down_returns_503`, `test_weather_stale_cache_when_upstream_fails`; fill `worksheets/external_api_failure.md` (timeout / 500 / malformed JSON / 429 — add a test for each row if time allows). | 3 tests green; site down → `{"error":{"code":"weather_service_unavailable",…}}` |
| **truyen_lp** | **H1** `GET /v1/offices` | `offices.all_offices()` (sorted by name) + unit test in a new file `tests/test_offices_all.py`; `OfficeOut` schema in `schemas.py`; endpoint `@app.get("/v1/offices", response_model=list[OfficeOut])` returning `[asdict(o) for o in service.offices()]`; 2 tests in `test_api.py` (status 200; one item named `"Library"`). Add the row to `api_contract.md` and a curl line to `curl_tests.sh`. | 2 tests green; list sorted by name |

Shared by everyone:
- **Individually** (not merged into the team repo): warm-up P1–P5 in `lab04/practice`, and the
  **H2 reflection** (5 lines: `service.handle()` vs `POST /v1/chat`) — submit on the LMS.
- Run `bash api-tests/curl_tests.sh` against your running server before opening your PR; paste the output.
- Type hints, `ruff check` clean, append AI use to `docs/ai-use-log.md`.
- Review pairs: vy_th↔dieu_sp, nhat_npm↔truyen_lp, nhat_dm↔long_th; han_htg reviews the scaffold-dependent PRs.

## 4. Order of work (merge order)

1. **Day 1 — foundation (blocking, small PRs, merge the same day):**
   long_th `config + deps` → nhat_dm `models + respond()` → han_htg `assistant_api scaffold + test fixtures`.
   Everyone agrees on §2 before coding.
2. **Days 2–4 — endpoints in parallel** (each only touches their own function in `main.py` and their own
   section of `test_api.py`, so merge conflicts stay trivial):
   vy_th (T1 + F), dieu_sp (T2 + T3), nhat_npm (T4), truyen_lp (H1).
3. **Day 5 — integration (long_th):** merge, full `pytest` + `ruff check` + `curl_tests.sh` on `main`,
   README check, tag `v0.4-api`. Deadline: pushed before next week's class.

Expected result on `main`: all Week 3 tests + the 9 prof tests in `test_api.py` (bonus test un-skipped)
+ the 2 H1 tests + new unit tests — **0 skipped, 0 failed**.
