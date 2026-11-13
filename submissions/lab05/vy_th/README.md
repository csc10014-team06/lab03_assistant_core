# Lab 5 — vy_th

Individual submission. Change **only this folder** in your PR. Rules: `docs/team-plan-lab05.md`.

## Files (copy the practice files here, see `../README.md`)
- [x] `my_answers.sql` — Q1–Q10 (must), Q11–Q15 (should)
- [x] `school_repo.py` — D1–D3 (must), including `test_d1_no_sql_injection`
- [ ] `h2.md` — H2 (should): one more useful question about the assistant data, its query, and the pasted result
- [x] `make_school_db.py`, `check.py`, `test_school_repo.py` — copied unchanged
- [x] No `school.db` committed

## Results (paste the real output)
`python check.py`:

```
Score: 15/15
```

`pytest -q test_school_repo.py`:

```
5 passed in 0.01s
```

## Reflection (optional, 2–3 lines)
JOIN and GROUP BY were the most challenging parts for me, especially understanding how to group rows and calculate aggregate values.
I learned how to use SQL placeholders (`?`) in Python to prevent SQL injection.
Running `check.py` and pytest helped me identify mistakes and verify my solutions.

## AI use

- **Tool:** ChatGPT (OpenAI)
- **Date:** 2026-11-13
- **Purpose:** Used AI as a learning assistant for Lab 05 SQL and Python database exercises.
- **How I used AI:** Asked for step-by-step explanations of SQL queries Q1–Q15, including `JOIN`, `GROUP BY`, `ORDER BY`, and aggregate functions. Used AI guidance to understand parameterized SQL queries, SQLite connections, and database operations in Python for D1–D3. Also received guidance on writing the H2 query to identify the busiest chatbot hour.
- **What I completed:** Wrote the SQL queries and Python database functions, tested the implementations, and corrected errors based on test results.
- **Verification:** `python check.py` returned **15/15**, and `python -m pytest -q test_school_repo.py` returned **5 passed**.
- **AI usage log:** Detailed prompts, retained work, and modifications are documented under **Member: vy_th — Session 3: Lab 5 Individual SQL and Python Practice** in `docs/ai-use-log.md`.
