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

## Member: dieu_sp

### Session: Lab 4 Feedback Endpoints (T2/T3)
- **Date**: 2026-11-07
- **Tool**: Claude Code (Claude Opus 5.5)
- **Prompt**: Implement issue #17 (T2 `POST /v1/feedback`, T3 `GET /v1/feedback` admin) following `docs/team-plan-lab04.md`.
- **Kept**: The starter's 3-line T2 body (in-memory `feedback_store`, `id = len + 1`, UTC `created_at`) and the 1-line T3 body relying on the existing `require_admin` dependency.
- **Changed**: Added the missing `datetime` import, removed the now-unused `noqa`, pasted the starter's `test_feedback_roundtrip` and `test_feedback_rating_out_of_range` unchanged into `tests/test_api.py`, filled the feedback rows of `worksheets/api_contract.md`, and verified 201 / 422 / 401 / 200 with `api-tests/curl_tests.sh`.

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
- **Prompt**: Help with completing `school_repo.py` (the D1-D3 functions, including the `transcript` JOIN) and running `pytest`.
- **Kept**: TO COMPLETE by long_th: what you kept from its suggestions.
- **Changed**: TO COMPLETE by long_th: what you changed or wrote yourself, and which answers (if any) came from it.
