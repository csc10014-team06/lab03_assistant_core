# Lab 6 — nhat_dm

Individual submission. Change **only this folder** in your PR. Rules: `docs/team-plan-lab06.md`.
Branch `lab6/nhat_dm` · PR title `Lab 6 – nhat_dm – A1/A2 + comparison` · **your H1 ids: E41–E45** (Member 5).

## Checklist (`python submissions/lab06/check.py nhat_dm` checks all of it)
- [x] **T1** `mini_search.py` — S1–S3 TODOs done; `pytest -q test_mini_search.py` → `4 passed` (do not edit the test)
- [x] **T2/T3** A2 grounding check + A1 abstain — already in `lab06/starter` (`llm.py` → `parse_draft`,
      `rag/answerer.py`); be able to explain both; `cd lab06/starter && pytest -q` → `42 passed`
- [x] **T4** `path_comparison.md` — output of `python eval/compare_paths.py` + exactly 3 sentences (a)(b)(c)
- [x] **T5** `h1_cases.jsonl` — 5 lines, ids E41–E45: 3 `expect_source` (chunk ids from `lab06/starter/data/kb/`),
      2 `"expect_abstain": true` (one out-of-scope, one about another person); re-run table + 1 sentence in `path_comparison.md`
- [x] **T6** `reflection.md` — 5 lines, your own words
- [ ] **T7** (bonus) `bonus.md` — Ollama run or H3 notes
- [x] No `.env`, `.venv/`, `*.db` or API key committed

## Results (paste the real output)

`pytest -q test_mini_search.py`:

```
4 passed in 0.04s
```

`python submissions/lab06/check.py nhat_dm` (last line):

```
Individual points found by this script: 6/6  (+ A1/A2 4 pts in lab06/starter, + bonus)
```

## AI use
Logged in `docs/ai-use-log.md`: yes
