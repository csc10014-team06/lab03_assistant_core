# AI Use Log

Record of AI-assistant usage across the refactoring process (as required by `docs/team-plan.md`).

---
## Member: han_htg 

### Session 1: CLI and Skeleton Setup
- **Tool:** Gemini
- **Usage:** Generated scaffold for `cli.py` using `argparse` with REPL and structured logging support; configured `pyproject.toml` and CLI unit tests.
- **Human contribution:** Kept CLI structure and REPL logic; updated imports to match team interface contracts; ensured no API keys or sensitive data leak into logs; verified via `pytest tests/test_cli.py -v` (4 passed) and `ruff check .` (all clean).

### Session 2: Integration, Documentation, CI & Worksheets
- **Tool:** Antigravity (Gemini 3.8 Flash Medium)
- **Usage:** Generated comprehensive English `README.md` (installation, configuration, one-shot/REPL usage, testing), configured GitHub Actions CI workflow (`.github/workflows/ci.yml`), and drafted the Before/After maintainability comparison and three-sentence summary in `worksheets/before_after_maintainability.md`.
- **Human contribution:** Verified documentation against codebase CLI options and environment variables; validated CI matrix and workflow syntax; verified all 227 tests pass and linter remains completely clean.

### Session 3: Lab 4 Web API Scaffold & Contract Setup
- **Tool:** Antigravity (Gemini 3.8 Flash Medium)
- **Usage:** Scaffolded `assistant_api` package structure, adjusted imports in `main.py` to match `assistant_core` modules (`cli`, `config`, `models`, `service`), configured `api-tests/curl_tests.sh` and Postman collection, copied worksheets (`api_contract.md`, `external_api_failure.md`), configured API fixtures and health check in `tests/test_api.py`, and added "Run the API" documentation to `README.md`.
- **Human contribution:** Verified endpoint routing structure against team contract; tested `/health` and OpenAPI `/docs` specification; ensured backward compatibility with Lab 3 tests.

### Session 4: Lab 5 Database Foundation & Individual SQL/Python Practice
- **Date:** 2026-11-13
- **Tool:** Gemini
- **Usage:** Guided adaptation of Lab 5 database foundation files (`assistant_api/db.py`, `sql/migrations/`, `scripts/migrate.py`, `scripts/seed.py`) to the team's flat layout, drafted the `Database` setup section for `README.md`, and assisted with individual SQL queries (`Q1–Q15`, `H2`) and parameterized `sqlite3` repository functions (`D1–D3`).
- **Human contribution:** Verified flat-layout imports and editable installation (`pip install -e .`); resolved Ruff `F841` warning in `list_feedback` while preserving `R1`/`R2` placeholders for teammates; tested idempotent migrations twice (`python scripts/migrate.py assistant.db`); verified individual practice locally via `python check.py` (`Score: 15/15`) and `pytest -q test_school_repo.py` (`5 passed`) while keeping `*.db` files untracked.

## Member: vy_th
### Session 1: Lab 3 Data Loader Implementation and Testing
- **Date**: 2026-10-26
- **Tool**: ChatGPT
- **Prompt**: "Help me implement and test the CSV/JSON data loader for the Lab 3 assistant_core refactoring project."
- **Kept**: The implementation of `load_offices()` and `load_handbook()`, data models (`Office`, `Rule`), input validation, exception handling with `DataLoadError`, and unit tests in `tests/test_data_loader.py`.
- **Changed**:
  1. Added validation for required CSV headers and office records.
  2. Validated handbook JSON structure and rule fields before constructing objects.
  3. Added error handling for missing files, malformed data, and invalid field values.
  4. Organized the implementation with type hints and frozen dataclasses.
  5. Reviewed Ruff warnings and refined the code to follow project conventions.
- **Verification**: Ran 9 data-loader unit tests successfully and checked Ruff for code quality.

### Session 2: Lab 4 Chat Endpoint and Rate Limiting
- **Date**: 2026-11-07
- **Tool**: ChatGPT
- **Prompt**: "Guide me through implementing T1 POST /v1/chat and Part F rate limiting according to docs/team-plan-lab04.md."
- **Kept**: The chat endpoint implementation using `AssistantService.respond(Message(...))`, UUID-based request IDs, per-client rate limiting with HTTP 429 responses, and three API tests covering tuition calculation, request validation, and rate limiting.
- **Changed**:
  1. Used `service.respond()` instead of the starter's `service.handle()` to match the team's Lab 4 interface.
  2. Integrated rate limiting into the existing `chat()` endpoint without modifying other members' endpoints.
  3. Recreated the Python virtual environment after identifying that the shell was using Homebrew Python instead of the project's virtual environment.
  4. Fixed import formatting using Ruff.
  5. Separated the chat endpoint, rate limiting, and API tests into three Git commits.
- **Verification**: All three targeted API tests passed, and Ruff reported `All checks passed!`.

## Member: nhat_dm

### Session: Lab 4 Service Bridge & Data Models
- **Date**: 2026-11-06
- **Tool**: Antigravity (Gemini 3.8 Flash Medium)
- **Prompt**: Implement models.py, AssistantService.respond(), and AssistantService.offices() according to docs/team-plan-lab04.md and issue #14.
- **Kept**: Pydantic models for Intent, Message, Source, Response; respond() routing logic for greeting, fee, office, handbook rule, unknown intent, and degraded state on LLMError; offices() stand-in delegation; comprehensive test suite in tests/test_models.py.
- **Changed**:
  1. Enforced thousands separators on fee responses for API compatibility (`9,450,000 VND.`).
  2. Isolated CLI commands (`save`, `history`, `stats`) from HTTP execution to prevent unauthorized filesystem access or internal state leaks.
  3. Ensured `handle()` and all Week 3 tests remain completely untouched and green.

## Member: nhat_npm

### Session: Lab 4 Weather Endpoint (T4)
- **Date**: 2026-11-07
- **Tool**: OpenAI Codex
- **Prompt**: "Merge new content from main into our branch" and implement the assigned T4 weather endpoint.
- **Kept**: The scaffold contract: return client weather results, preserve stale-cache responses, and map `ExternalServiceError` to the standard HTTP 503 error.
- **Changed**: Implemented `/v1/weather`, added its three required API tests, and completed `worksheets/external_api_failure.md` using the provided `WeatherClient` behavior.

## Member: dieu_sp

### Session: Lab 4 Feedback Endpoints (T2/T3)
- **Date**: 2026-11-07
- **Tool**: Claude Code (Claude Opus 5.5)
- **Prompt**: Implement issue #17 (T2 `POST /v1/feedback`, T3 `GET /v1/feedback` admin) following `docs/team-plan-lab04.md`.
- **Kept**: The starter's 3-line T2 body (in-memory `feedback_store`, `id = len + 1`, UTC `created_at`) and the 1-line T3 body relying on the existing `require_admin` dependency.
- **Changed**: Added the missing `datetime` import, removed the now-unused `noqa`, pasted the starter's `test_feedback_roundtrip` and `test_feedback_rating_out_of_range` unchanged into `tests/test_api.py`, filled the feedback rows of `worksheets/api_contract.md`, and verified 201 / 422 / 401 / 200 with `api-tests/curl_tests.sh`.

## Member: truyen_lp

### Session: Lab 5 SQL/Python Practice & Assistant Analytics Queries (F1–F3)
- **Date**: 2026-11-14
- **Tool**: Antigravity (Gemini 4 Hydrogen)
- **Prompt**: "Review docs/team-plan-lab05.md and issue #35, plan and implement truyen_lp's Lab 5 individual practice (Q1–Q15, D1–D3, H2) and team analytics queries (sql/my_queries.sql F1–F3)."
- **Kept**: Practice SQL queries `Q1–Q15` in `submissions/lab05/truyen_lp/my_answers.sql`, parameterized `sqlite3` functions `D1–D3` in `submissions/lab05/truyen_lp/school_repo.py`, `H2` quality-vs-feedback query in `h2.md`, and `SELECT`-only `F1–F3` queries in `sql/my_queries.sql`.
- **Changed**:
  1. Kept `feat/lab05-practice-truyen_lp` strictly scoped to `submissions/lab05/truyen_lp/` and logged AI usage in `feat/lab05-queries-truyen_lp` to satisfy the practice PR folder rule and avoid conflicts.
  2. Added `AND i.topic IS NOT NULL` in F3 so thumbs-down counts rank named handbook topics (`H26-*`) rather than grouping `NULL` non-rule topics.
  3. Verified `check.py` (`Score: 15/15`), `pytest -q test_school_repo.py` (`5 passed`), `ruff check .`, full `pytest` (`303 passed`), and all F1–F3/H2 queries against a 300-row seeded `assistant.db` (using an in-memory R1 shim while PR #45 is pending).
