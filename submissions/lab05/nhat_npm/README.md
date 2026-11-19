# Lab 5 - nhat_npm

Individual submission. This branch changes only this folder, as required by `docs/team-plan-lab05.md`.

## Files
- [x] `my_answers.sql` - Q1-Q15
- [x] `school_repo.py` - D1-D3, with parameterized SQL
- [x] `h2.md` - an additional assistant-data question, query, and result
- [x] `make_school_db.py`, `check.py`, `test_school_repo.py` copied unchanged
- [x] `school.sql` and `expected.json` copied as checker/database inputs
- [x] `school.db` is generated locally and ignored; it is not submitted

## Results

`python check.py`:

```
Score: 15/15
```

`pytest -q test_school_repo.py`:

```
5 passed
```

## Reflection

The JOIN in the transcript query was the hardest part because it has to connect each enrollment to the matching course. Bound placeholders keep input values separate from SQL, and GROUP BY lets SQLite count each program or course cleanly.

## AI use

Yes. Usage is recorded in `docs/ai-use-log.md` in the separate team contribution branch.