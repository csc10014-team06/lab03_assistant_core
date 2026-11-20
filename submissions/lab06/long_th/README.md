# Lab 6 — long_th

Individual submission. Change **only this folder** in your PR. Rules: `docs/team-plan-lab06.md`.
Branch `lab6/long_th` · PR title `Lab 6 – long_th – A1/A2 + comparison` · **your H1 ids: E21–E25** (Member 1).

## Checklist (`python submissions/lab06/check.py long_th` checks all of it)
- [x] **T1** `mini_search.py` — S1–S3 TODOs done; `pytest -q test_mini_search.py` → `4 passed` (do not edit the test)
- [x] **T2/T3** A2 grounding check + A1 abstain — already in `lab06/starter` (`llm.py` → `parse_draft`,
      `rag/answerer.py`); be able to explain both; `cd lab06/starter && pytest -q` → `42 passed`
- [x] **T4** `path_comparison.md` — output of `python eval/compare_paths.py` + exactly 3 sentences (a)(b)(c)
- [x] **T5** `h1_cases.jsonl` — 5 lines, ids E21–E25: 3 `expect_source` (chunk ids from `lab06/starter/data/kb/`),
      2 `"expect_abstain": true` (one out-of-scope, one about another person); re-run table + 1 sentence in `path_comparison.md`
- [x] **T6** `reflection.md` — 5 lines, your own words
- [x] **T7** (bonus) `bonus.md` — Ollama run or H3 notes
- [x] No `.env`, `.venv/`, `*.db` or API key committed

## Results (paste the real output)

`pytest -q test_mini_search.py`:

```
4 passed in 0.01s
```

`python submissions/lab06/check.py long_th` (last line):

```
[PASS] T1 mini search 2/2 · [PASS] T4 comparison 1/1 · [PASS] T5 H1 cases 2/2 · [PASS] T5 re-run output
[PASS] T6 reflection 1/1 · [PASS] hygiene · [PASS] T7 bonus (H3)
Individual points found by this script: 6/6, bonus +1  (+ A1/A2 4 pts in lab06/starter)
```

`cd lab06/starter && pytest -q` → `42 passed`; `pytest -q tests/test_rag.py -k "citation or abstain"` → `2 passed`.

## AI use
- **Tool:** Claude Code. Logged here because this PR may only change this folder; to be copied into `docs/ai-use-log.md`
  with the team's log update.
- **Used for:** S1–S3 in `mini_search.py`; choosing and checking the 5 H1 cases against the real service (it traced why
  E23 goes to the fee tool and why the privacy guard misses E25); the 3 sentences and the failure sentence; running the
  H3 experiment and writing `bonus.md`; a first draft of the reflection.
- **Checked by me:** `pytest -q test_mini_search.py` (4 passed), `python submissions/lab06/check.py long_th` (all PASS),
  the pasted tables are the real `compare_paths.py` output, the H3 change was reverted (not in this PR).
