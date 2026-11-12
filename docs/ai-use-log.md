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

## Member: vy_th

- **Tool**: ChatGPT
- **Usage**: Reviewed CSV/JSON loading logic, validation, exception handling, pytest tests, and Ruff warnings.
- **Human contribution**: Implemented and revised the loaders, checked suggestions, and ran tests locally.

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
