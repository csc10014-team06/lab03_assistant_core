# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 (`RATE`, line 8), but only by editing the source; `RETAKE_RATE` is a second constant | |
| Can you run the tests without internet or an API key? | There are no real tests: `--test` only prints answers. The fake `llm()` fails 10 % of the time at random and sleeps 0.2 s | |
| What happens if `handbook.json` is missing? | Bare `except` prints "could not load handbook" and continues with an empty handbook, so every rule question answers "Sorry I dont know" | |
| Is any secret printed or logged? | Yes: the hard-coded `API_KEY` is printed on every LLM call (`DEBUG = True` by default), together with the user's prompt | |
| How long does it take a new teammate to find the fee logic? | It is buried in lines 60–75 of the 56-line `handle()` | |
| Number of global variables | 9 (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `history`, `offices`, `handbook`, `BASE`); 3 are mutable state | |
| Number of bare `except:` blocks | 3 (lines 26, 30, 136) | |
| Lines in the longest function | 56 (`handle`, lines 44–99) | |
| `ruff check` issues | 13 (ruff 0.16.9, default rules) | |
| Can you swap the LLM without touching the service? | No: `handle()` calls the module-level `llm()` directly | |

**Three sentences:** what improved most, what got more complex, and what you would still change.
