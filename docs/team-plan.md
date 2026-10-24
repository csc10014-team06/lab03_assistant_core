# Lab 3 — Team plan: refactoring `assistant_monolith.py` (7 members)

Goal: turn `monolith/assistant_monolith.py` into a small, tested Python package
with the **same observable behaviour**, then fill in the two worksheets.

## 1. Target layout

```
assistant_core/
  __init__.py
  config.py        # long_th  settings, constants, secrets from env
  data_loader.py   # vy_th  read offices.csv / handbook.json
  fees.py          # dieu_sp  parse credits/retakes, compute tuition
  offices.py       # truyen_lp  office lookup
  handbook.py      # truyen_lp  rule search (retrieval)
  llm.py           # nhat_npm  LLM interface + fake/offline client
  service.py       # nhat_dm  AssistantService: routing, history, stats, save
  cli.py           # han_htg  REPL / one-shot entry point, logging setup
  data/            # moved from monolith/data
tests/
  test_characterization.py  # long_th  golden tests of the OLD behaviour
  test_config.py            # long_th
  test_data_loader.py       # vy_th
  test_fees.py              # dieu_sp
  test_offices.py, test_handbook.py  # truyen_lp
  test_llm.py               # nhat_npm
  test_service.py           # nhat_dm
  test_cli.py               # han_htg
pyproject.toml, README.md   # han_htg
docs/ai-use-log.md          # everyone appends
```

## 2. Interface contracts (agree on these FIRST — day 1)

Everyone codes against these signatures, so work can happen in parallel.
Change them only via a PR that all affected owners approve.

```python
# config.py
@dataclass(frozen=True)
class Settings:
    credit_rate: int = 450_000          # VND per credit
    retake_multiplier: float = 1.5
    max_credits: int = 30
    model: str = "gpt-small"
    api_key: str | None = None          # from env ASSISTANT_API_KEY, never hard-coded
    debug: bool = False
    data_dir: Path = <package>/data
    history_dir: Path = <cwd>
def load_settings(env: Mapping[str, str] = os.environ) -> Settings: ...

# data_loader.py
@dataclass(frozen=True)
class Office:  name: str; room: str; hours: str
@dataclass(frozen=True)
class Rule:    id: str; title: str; text: str
class DataLoadError(Exception): ...
def load_offices(path: Path) -> dict[str, Office]: ...   # key = lower-case name
def load_handbook(path: Path) -> list[Rule]: ...

# fees.py
@dataclass(frozen=True)
class FeeQuery: credits: int; retakes: int
def parse_fee_query(text: str) -> FeeQuery: ...           # credits=0 if none found
def compute_tuition(q: FeeQuery, s: Settings) -> int: ...
class TooManyCreditsError(ValueError): ...

# offices.py / handbook.py
def find_office(text: str, offices: dict[str, Office]) -> Office | None: ...
def best_rule(text: str, rules: list[Rule], min_score: int = 1) -> Rule | None: ...

# llm.py
class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...
class LLMError(Exception): ...
class FakeLLM:   ...   # deterministic, no network, no sleep — used by tests
class DemoLLM:   ...   # reproduces the monolith's "Here is what I found: ..." reply

# service.py
class AssistantService:
    def __init__(self, settings, offices, rules, llm: LLMClient): ...
    def handle(self, message: str) -> str: ...
    def stats(self) -> dict[str, int]: ...
    def save_history(self, filename: str) -> Path: ...
```

## 3. Assignments

| Owner | Module(s) | Main tasks | Done when |
|---|---|---|---|
| **long_th** | `config.py`, `tests/test_characterization.py` | Move every magic number/flag into `Settings`; read API key from env var (add `.env.example`, never commit real keys). **Before anyone refactors**, write characterization tests that pin the monolith's current outputs (the 6 cases in `test()` + edge cases). | Changing the rate = 1 place; characterization tests pass against old AND new code |
| **vy_th** | `data_loader.py` | Replace both bare `except:` with specific exceptions; use `with open(...)` / `pathlib`; parse CSV with `DictReader` into `Office`; validate handbook entries into `Rule`; log (not print) a clear warning when a file is missing; move `data/` into the package. | Missing/broken file → defined behaviour + test |
| **dieu_sp** | `fees.py` | Extract fee parsing & calculation (monolith lines 60–75) into pure functions; no globals; handle "retake"/"retakes", "?" etc.; decide how `"coffee"` vs `"fee"` keyword matching is handled (word match). | Parametrized tests incl. 0 credits, >30, retakes, 18+2 = 13 050 000 VND |
| **truyen_lp** | `offices.py`, `handbook.py` | Extract office lookup (lines 77–80) and keyword scoring search (lines 82–91); make scoring a pure function; keep tie-breaking identical; return dataclasses not raw rows. Later: implement the **AI-extension feature** (exam absence answer) — see §5. | Tests for hit, miss, tie, case-insensitivity |
| **nhat_npm** | `llm.py` | Define `LLMClient` protocol; `FakeLLM` for tests (no `sleep`, no `random`); `DemoLLM` keeps current behaviour with injectable RNG/timeout; raise `LLMError` instead of bare `Exception`; **never log the API key**; log prompts only at DEBUG and truncated. | Tests run offline, deterministic, with no key |
| **nhat_dm** | `service.py` | `AssistantService` class replacing `handle()`, `stats()`, `save_history()` and the `history` global; route intents by calling dieu_sp/truyen_lp/nhat_npm functions; LLM failure → fall back to rule text (as today); fix `save` path traversal (`save ../../x`) by restricting to `history_dir`; `stats()` returns a dict, formatting stays in CLI. | All characterization tests green via the service |
| **han_htg** | `cli.py`, `pyproject.toml`, `README.md`, CI | `argparse` entry point (one-shot + REPL + `quit`/EOF); `logging` config with `--debug` flag replacing `DEBUG` prints/timing; `pyproject.toml` with ruff + pytest config; README (install, run, test); optional GitHub Actions running `ruff check` + `pytest`. Owns **integration**: final merge, delete/archive monolith usage. | `python -m assistant_core "hi"` works; `ruff check` and `pytest` clean |

Shared by everyone:
- Unit tests for your own module (target: every public function tested).
- Type hints + short docstrings; `ruff check` clean before opening a PR.
- Append any AI-assistant use to `docs/ai-use-log.md` (who, tool, prompt, what you kept/changed).
- Review at least one other member's PR (suggested pairs: long_th↔vy_th, dieu_sp↔truyen_lp, nhat_npm↔nhat_dm, han_htg reviews the integration PRs).

## 4. Timeline

1. **Day 1 (all, ~30 min meeting):** agree on §2 contracts. long_th opens the characterization-test PR first; han_htg opens the skeleton PR (`pyproject.toml`, empty modules, ruff/pytest config). Everyone else branches from the skeleton.
2. **Days 2–4 (parallel):** each member implements their module + tests on `feature/<module>` and opens a PR. The modules of vy_th, dieu_sp, truyen_lp and nhat_npm have no dependencies on each other; nhat_dm can start immediately using `FakeLLM` and hand-built `Office`/`Rule` fixtures.
3. **Day 5 (integration, nhat_dm + han_htg lead):** wire everything in `cli.py`; characterization tests must pass unchanged; fix ruff issues.
4. **Day 6 (worksheets):**
   - `worksheets/ai_extension_review.md` — **truyen_lp** (feature) + **nhat_npm** (reviews the AI-generated code against the checklist: interfaces, deps, secrets, logging of user data, tests).
   - `worksheets/before_after_maintainability.md` — **long_th** collects numbers (globals, bare excepts, longest function, `ruff check` counts before/after); **han_htg** writes the three-sentence summary; whole team reviews.

## 5. Known problems in the monolith (checklist for owners)

| Problem | Where | Owner |
|---|---|---|
| Hard-coded API key, and it is printed in debug output | lines 6, 37 | long_th, nhat_npm |
| 5 module-level mutable globals (`history`, `offices`, `handbook`, …) | lines 11–13 | nhat_dm |
| Bare `except:` (×3) swallow all errors | lines 26, 30, 136 | vy_th, han_htg |
| Files opened without `with`; handbook file never closed | lines 20, 29, 119 | vy_th, nhat_dm |
| `handle()` is ~55 lines doing 7 jobs | lines 44–99 | dieu_sp, truyen_lp, nhat_dm |
| Substring keyword match (`"coffee"` → fee question) | lines 60, 78, 107 | dieu_sp, truyen_lp |
| Fee logic duplicated between `handle()` and `stats()` intent detection | lines 60, 107 | nhat_dm (single intent classifier) |
| Random 10 % failure + `sleep` makes behaviour/tests non-deterministic | lines 38–40 | nhat_npm |
| `save <name>` writes any user-chosen path (path traversal) | lines 56–57, 119 | nhat_dm |
| User messages (possibly personal data) echoed to logs | line 37 | nhat_npm |
| Manual `test()` prints instead of asserting | lines 148–155 | long_th |
| `print` used for diagnostics instead of `logging` | throughout | han_htg |
