# Lab 5 — truyen_lp

Individual submission. Change **only this folder** in your PR. Rules: `docs/team-plan-lab05.md`.

## Files (copy the practice files here, see `../README.md`)
- [x] `my_answers.sql` — Q1–Q10 (must), Q11–Q15 (should)
- [x] `school_repo.py` — D1–D3 (must), including `test_d1_no_sql_injection`
- [x] `h2.md` — H2 (should): one more useful question about the assistant data, its query, and the pasted result
- [x] `make_school_db.py`, `check.py`, `test_school_repo.py` — copied unchanged
- [x] No `school.db` committed

## Results (paste the real output)

`python check.py`:

```
Score: 15/15
```

`pytest -q test_school_repo.py`:

```
5 passed in 0.02s
```

## Reflection (optional, 2–3 lines)
Handling `LEFT JOIN` filtering in Q15 (placing `e.course_code = 'CSC10014'` in `ON` rather than `WHERE` so unmatched students are preserved) and remembering `IS NULL` vs `=` were the trickiest parts. Parameterized `?` placeholders in `school_repo.py` kept SQL injection prevention straightforward.

## AI use
Logged in `docs/ai-use-log.md`: yes (added in the Part B team PR `feat/lab05-queries-truyen_lp` so this practice PR touches only `submissions/lab05/truyen_lp/`)
