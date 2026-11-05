# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 (`RATE`, line 8), but only by editing the source; `RETAKE_RATE` is a second constant | Exactly 1 place: `Settings.credit_rate` in `config.py`, or override dynamically via the `ASSISTANT_CREDIT_RATE` environment variable without code changes. |
| Can you run the tests without internet or an API key? | There are no real tests: `--test` only prints answers. The fake `llm()` fails 10 % of the time at random and sleeps 0.2 s | Yes: all 227 unit and characterization tests run offline and deterministically in ~2 seconds using `FakeLLM` without external network, API keys, or random delays. |
| What happens if `handbook.json` is missing? | Bare `except` prints "could not load handbook" and continues with an empty handbook, so every rule question answers "Sorry I dont know" | `load_handbook()` raises a structured `DataLoadError`; the CLI logs a clear warning via `logging` and falls back gracefully to an empty rule list. |
| Is any secret printed or logged? | Yes: the hard-coded `API_KEY` is printed on every LLM call (`DEBUG = True` by default), together with the user's prompt | No: secrets are supplied exclusively via environment variables (`ASSISTANT_API_KEY`), excluded from dataclass representation (`repr=False`), and never logged. |
| How long does it take a new teammate to find the fee logic? | It is buried in lines 60–75 of the 56-line `handle()` | Under a minute: cleanly isolated in `assistant_core/fees.py` as pure functions (`parse_fee_query`, `compute_tuition`). |
| Number of global variables | 9 (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `history`, `offices`, `handbook`, `BASE`); 3 are mutable state | 0 mutable globals; all state and dependencies are encapsulated inside immutable `Settings` and `AssistantService` instances. |
| Number of bare `except:` blocks | 3 (lines 26, 30, 136) | 0 bare `except:` blocks; all exception handlers catch explicit, domain-specific exception types. |
| Lines in the longest function | 56 (`handle`, lines 44–99) | 48 lines (`handle` in `assistant_core/service.py`). |
| `ruff check` issues | 13 (ruff 0.16.9, default rules) | 0 issues (`ruff check .` passes completely clean). |
| Can you swap the LLM without touching the service? | No: `handle()` calls the module-level `llm()` directly | Yes: `AssistantService` accepts any client conforming to the `LLMClient` protocol via dependency injection. |

**Three sentences:** what improved most, what got more complex, and what you would still change.

1. **What improved most:** Testability and maintainability improved the most through modular separation of concerns, complete removal of mutable global state and bare except blocks, and deterministic offline testing via dependency injection.
2. **What got more complex:** Project architecture and wiring grew slightly more complex due to introducing explicit protocols, frozen dataclasses, error hierarchies, and dependency injection across isolated domain modules.
3. **What you would still change:** I would replace the substring and token-overlap keyword matching in `handbook.py` and `offices.py` with semantic vector embeddings to handle paraphrase queries and typos more robustly.
