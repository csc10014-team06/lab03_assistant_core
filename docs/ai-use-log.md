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

## Member: truyen_lp

### Session 1: Planning and Architecture Review
- **Date**: 2026-10-26
- **Tool**: Antigravity (Gemini 3.8 Flash High)
- **Prompt**: "Bạn hãy đọc qua docs/team-plan.md, mình là truyen_lp. Bạn hãy xem và lập plan thực hiện kế hoạch cho mình."
- **Kept**: Detailed execution plan structuring offices.py lookup, handbook.py scoring, tie-breaking guarantees, dataclass contracts, and test plans.
- **Changed**: Refined tokenization boundary punctuation stripping in `handbook.py` so trailing punctuation (e.g. `thesis?`) does not prevent keyword matching, while strictly preserving monolith tie-breaking logic.

### Session 2: AI-Extension Feature (Exam Absence)
- **Date**: 2026-10-26
- **Tool**: Antigravity (Gemini 3.8 Flash High)
- **Prompt**: "Write a Python function in handbook.py that extracts the exam absence rule and returns a direct answer with the deadline for submitting evidence to the Training Office."
- **Kept**: Core intent of finding rule and providing deadline answer.
- **Changed**:
  1. Replaced hardcoded text with dynamic regex extraction against `Rule.text` from the handbook dataset (extracting both office and deadline dynamically).
  2. Replaced untyped signature returning string on error with `Rule | None` / `str | None` type hints and proper docstrings.
  3. Replaced fragile `r.title` check with canonical ID `_EXAM_ABSENCE_RULE_ID` lookup and pure `best_rule` keyword fallback.
- **Review documented in**: `worksheets/ai_extension_review.md`.

### Session 3: Peer Review Feedback & Hardening
- **Date**: 2026-10-26
- **Tool**: Antigravity (Gemini 3.8 Flash High)
- **Prompt**: "Review PR feedback from dieu_sp and address all 5 points."
- **Kept**: Feedback points from dieu_sp.
- **Changed**:
  1. Upgraded `find_office` in `offices.py` to use word-boundary matching `\b{key}\b` (addressing monolith line 78 substring bug).
  2. Extracted both destination office and deadline dynamically via named groups in `_ABSENCE_PATTERN` to strictly uphold single source of truth.
  3. Added module constant `_EXAM_ABSENCE_RULE_ID = "H26-7.2"`.
  4. Added unit tests for substring false positive rejection and dynamic office extraction.

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
