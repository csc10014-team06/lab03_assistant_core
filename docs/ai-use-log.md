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

### Session 5: Lab 6 RAG, Abstain, Grounding, Eval & H3 Bonus
- **Tool:** Gemini
- **Date:** 2026-11-20
- **Usage:** Assisted with implementing inverted index and top-k scoring in `mini_search.py` (S1–S3), explaining A1 abstain and A2 grounding checks, resolving local `.venv` dependency installation (`pydantic`), designing H1 evaluation cases (`E46–E50`), drafting the 3-sentence path comparison and open-book reflection, and analyzing the T7 Option H3 plural-stripping experiment.
- **Human contribution:** Verified all tests locally (`pytest -q test_mini_search.py` → 4 passed; `pytest -q tests/test_rag.py -k "citation or abstain"` → 2 passed); ran `compare_paths.py` on both the base 20 cases and custom H1 cases (`20/25` passing) and diagnosed why `E46` failed due to premature keyword routing on `"fee"`; tested T7 Option H3 (`tokenize` plural stripping) locally, observed the drop to `15/20` (`E20` false positive above `min_score`), reverted `index.py` to keep the PR scoped strictly to `submissions/lab06/han_htg/`, and validated all deliverables with `python submissions/lab06/check.py han_htg` (`6/6` + bonus).

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
### Session 3: Lab 5 Individual SQL and Python Practice
- **Date**: 2026-11-13
- **Tool**: ChatGPT (OpenAI)
- **Prompt**: Guide me step by step through Lab 5 SQL Q1–Q15, Python D1–D3, and H2 without giving complete solutions.
- **Kept**: The original practice starter files, SQL question markers, and provided tests.
- **Changed**: Completed SQL Q1–Q15, implemented D1–D3 using parameterized SQL, and wrote an H2 query about the busiest chatbot hour.
- **Verification**: `python check.py` — 15/15; `pytest -q test_school_repo.py` — 5 passed.

### Session 4: Lab 5 Chat Interaction Persistence
- **Date**: 2026-11-13
- **Tool**: ChatGPT (OpenAI)
- **Prompt**: Implement chat interaction persistence following docs/team-plan-lab05.md and help debug the API tests.
- **Kept**: The existing Lab 4 chat endpoint, rate limiting, and the provided Repository.record_interaction() implementation.
- **Changed**: Added database initialization, response latency measurement, and interaction metadata recording without storing raw messages. Added a persistence test using temporary SQLite.
- **Verification**: Full pytest — 304 passed; Ruff — all checks passed.

## Member: nhat_dm

### Session 1: Lab 4 Service Bridge & Data Models
- **Date**: 2026-11-06
- **Tool**: Antigravity (Gemini 3.8 Flash Medium)
- **Prompt**: Implement models.py, AssistantService.respond(), and AssistantService.offices() according to docs/team-plan-lab04.md and issue #14.
- **Kept**: Pydantic models for Intent, Message, Source, Response; respond() routing logic for greeting, fee, office, handbook rule, unknown intent, and degraded state on LLMError; offices() stand-in delegation; comprehensive test suite in tests/test_models.py.
- **Changed**:
  1. Enforced thousands separators on fee responses for API compatibility (`9,450,000 VND.`).
  2. Isolated CLI commands (`save`, `history`, `stats`) from HTTP execution to prevent unauthorized filesystem access or internal state leaks.
  3. Ensured `handle()` and all Week 3 tests remain completely untouched and green.

### Session 2: Lab 5 Team Persistence Tests
- **Date**: 2026-11-13
- **Tool**: Antigravity (Gemini 3.8 Flash Medium)
- **Prompt**: Implement tests/test_persistence.py covering restart persistence, 404 on unrecorded request_id, duplicate request_id handling, session hashing, raw session privacy, and idempotent migration execution.
- **Kept**: Contract for Repository and FastAPI application endpoints; tested against temporary SQLite databases using tmp_path.
- **Changed**:
  1. Verified that feedback created in one app instance persists in SQLite across restart to a new app instance.
  2. Verified that submitting feedback for unknown request_id returns 404 and writes zero rows to feedback table.
  3. Tested duplicate feedback submissions for the same request_id, preserving multiple entries with distinct auto-incremented IDs.
  4. Tested session hashing determinism and salt-dependence (multiple interactions within same session create 1 ChatSession row).
  5. Verified that raw session IDs and message text are never stored in the database.
  6. Verified that scripts/migrate.py runs multiple times safely without errors.
- **Verification**: All 316 tests green in pytest; Ruff check clean.
### Session 2: Lab 5 Individual SQL & Python Practice
- **Date**: 2026-11-13
- **Tool**: Antigravity (Gemini 3.8 Flash Medium)
- **Prompt**: Complete individual SQL practice Q1-Q15 on school.db, Python repository functions D1-D3 with parameterized queries, and extra question H2 with query and analysis.
- **Kept**: Completed `my_answers.sql` covering queries Q1–Q15; `school_repo.py` implementing `students_in_program`, `add_student`, `average_grade`, and `transcript`; crafted `h2.md` analyzing at-risk failure proportions across courses.
- **Verification**: Verified SQL answers via `python check.py` achieving `Score: 15/15`; verified `school_repo.py` via `pytest -q test_school_repo.py` (`5 passed`); verified that `school.db` remains untracked in Git; ensured code formatting adheres to team standards.

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

## Member: dieu_sp

### Session: Lab 5 practice (Part A) and feedback persistence R1/R2 (Part B)
- **Date**: 2026-11-13
- **Tool**: Claude Code (Claude Opus 5.5)
- **Prompt**: Complete issue #32 following `docs/team-plan-lab05.md`: individual practice in `submissions/lab05/dieu_sp/`, then R1 `add_feedback` / R2 `list_feedback` and replace the in-memory `feedback_store`.
- **Kept**: The starter's R1 body (add, commit, refresh, return) and its `create_app(..., repo=None)` wiring; the starter's `test_feedback_roundtrip` shape.
- **Changed**: R2 sorts by `created_at DESC, id DESC` so rows saved in the same clock tick keep a stable order; the default repository uses our `db_url` and `require_hash_salt()` settings; API tests use an in-memory database; added tests for the 404 and newest-first order; updated the feedback rows of `worksheets/api_contract.md`.
- **Verification**: `python check.py` → `Score: 15/15`, `pytest -q test_school_repo.py` → `5 passed`; full `pytest` → 305 passed, `ruff check .` clean; a manual run against a temp SQLite file showed 201 / 404 / 401 and the row still listed after re-creating the app.

## Member: long_th

### Session: Lab 4 config, dependencies and packaging (issue #13)
- **Date**: 2026-11-05
- **Tool**: Claude Code
- **Prompt**: Do the long_th tasks of the Lab 4 plan: add the API settings, merge FastAPI/httpx/uvicorn into the dependency files, package `assistant_api`, extend `.env.example`, add tests.
- **Kept**: Six new `Settings` fields read from `ASSISTANT_*` variables, the admin key hidden from `repr()`, validation raising `ConfigError`, pinned versions in `requirements.txt` and ranges in `pyproject.toml`, and `tests/test_config_api.py` (24 tests, no existing test modified).
- **Changed**: The AI-written commit was cherry-picked onto the member's own branch. `ruff check` and `pytest` were run against it (all clean) before it was pushed.

### Session: Lab 5 database settings and review of practice answers (issue #31)
- **Date**: 2026-11-12
- **Tool**: Claude Code
- **Prompt**: (1) Do the long_th config task of the Lab 5 plan: database URL, secret salt for hashing session ids, `sqlmodel` dependency. (2) Review my SQL Q1-Q15 and `school_repo.py` D1-D3 and check the commit on my branch. (3) Draft the H2 question and query (`submissions/lab05/long_th/h2.md`).
- **Kept**: `db_url` and `hash_salt` settings (salt hidden from `repr()`, minimum length, no default, `require_hash_salt()` failing loudly), `sqlmodel==0.0.22` pinned, and `tests/test_config_db.py` (17 tests, no existing test modified).
- **Changed**: Claude Code reviewed the practice answers (Q1-Q15, D1-D3; see the next entry for the other assistant used while writing them) and pointed out `con.commit;` (missing parentheses, so inserts were not saved), `credits >= 4` instead of `= 4` in Q6, a missing `ORDER BY` in Q8, and a wrongly named file (`my_answer.sql`). The member fixed the file name, the commit call and Q6; the AI added the Q8 `ORDER BY` and removed stray semicolons/whitespace. The scores in the folder README are the member's own `check.py` / `pytest` results. Claude Code also drafted the H2 question and its SQL query (validated for syntax on a stand-in table); the member ran it on their own seeded `assistant.db` and Claude Code transcribed the output from their terminal screenshot and wrote the short interpretation in `h2.md`. Claude Code also gave a small script to patch R1/R2 (from tutorial E.4/E.5) into the local starter `db.py` so that `seed.py` could run.

### Session: Lab 5 practice, editor assistant (Q1-Q15, D1-D3)
- **Date**: 2026-11-12
- **Tool**: Gemini (chat assistant in the code editor)
- **Prompt**: Help with `school_repo.py` (the `transcript` JOIN query, D3) and with running `pytest`.
- **Kept**: The code it suggested for `school_repo.py`, in particular the `transcript` JOIN query (D3), which is identical to the code shown in its chat panel. It also explained that the `pytest` failure came from an older system Python and how to recreate the virtual environment with Python 3.10.
- **Changed**: Used its suggestions and then tested them myself: `python check.py` gives 15/15 and `pytest -q test_school_repo.py` gives 5 passed. No other practice answers were taken from it.

## Member: nhat_npm

### Session: Lab 5 individual practice and privacy review
- **Date:** 2026-11-13
- **Tool:** OpenAI Codex
- **Prompt:** "Pull latest main, copy the Lab 5 materials, and complete Nhat_NPM's assigned tasks."
- **Kept:** The supplied SQL question markers, checker, repository tests, and Lab 5 database contracts.
- **Changed:** Implemented Q1-Q15 and D1-D3 in my individual folder, added H2 with a result from synthetic data, and completed the data-model/privacy review using the starter schema and tutorial.
- **Verification:** `python check.py` reported `Score: 15/15`; `pytest -q test_school_repo.py` reported `5 passed`. The H2 dataset has 300 synthetic interactions; a temporary runtime shim supplied the still-pending R1 feedback insert so the seed script could finish. No team implementation files were changed for the shim.

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
