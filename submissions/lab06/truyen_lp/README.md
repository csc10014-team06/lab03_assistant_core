# Lab 6 — truyen_lp

Individual submission. Change **only this folder** in your PR. Rules: `docs/team-plan-lab06.md`.
Branch `lab6/truyen_lp` · PR title `Lab 6 – truyen_lp – A1/A2 + comparison` · **your H1 ids: E31–E35** (Member 3).

## Checklist (`python submissions/lab06/check.py truyen_lp` checks all of it)
- [ ] **T1** `mini_search.py` — S1–S3 TODOs done; `pytest -q test_mini_search.py` → `4 passed` (do not edit the test)
- [ ] **T2/T3** A2 grounding check + A1 abstain — read them in `assistant_core/llm.py` (`parse_draft`) and
      `assistant_core/rag/answerer.py`; `pytest -q tests/test_rag.py -k "citation or abstain"` green
- [ ] **T4** `path_comparison.md` — table from `python eval/compare_paths.py` + exactly 3 sentences (a)(b)(c)
- [ ] **T5** `h1_cases.jsonl` — 5 lines, ids E31–E35: 3 `expect_source` (chunk ids from `assistant_core/data/kb/`),
      2 `"expect_abstain": true` (one out-of-scope, one about another person); re-run table + 1 sentence in `path_comparison.md`
- [ ] **T6** `reflection.md` — 5 lines, your own words
- [ ] **T7** (bonus) `bonus.md` — Ollama run or H3 notes
- [ ] No `.env`, `.venv/`, `*.db` or API key committed

## Results (paste the real output)

`pytest -q test_mini_search.py`:

```
__ passed
```

`python submissions/lab06/check.py truyen_lp` (last line):

```
Individual points found by this script: __/6
```

## AI use
Logged in `docs/ai-use-log.md`: yes / no / not used
