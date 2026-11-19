# Lab 5 — nhat_dm

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
Q1   OK  
Q2   OK  
Q3   OK  
Q4   OK  
Q5   OK  
Q6   OK  
Q7   OK  
Q8   OK  
Q9   OK  
Q10  OK  
Q11  OK  
Q12  OK  
Q13  OK  
Q14  OK  
Q15  OK  

Score: 15/15
```

`pytest -q test_school_repo.py`:

```
.....                                                                    [100%]
5 passed in 0.04s
```

## Reflection (optional, 2–3 lines)
What was hardest: Understanding when to use `LEFT JOIN` vs `JOIN` with aggregations (e.g., in Q12 and Q14 to make sure entities with 0 enrollments are preserved) and ensuring placeholder `?` syntax is strictly followed in Python to prevent SQL injection.

## AI use
Logged in `docs/ai-use-log.md`: yes
