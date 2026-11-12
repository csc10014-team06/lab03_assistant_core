# Lab 5 — individual submissions

One folder per member. **Each PR may change only your own folder.** Full rules: `docs/team-plan-lab05.md` (§1–§3).

| Folder | Member |
|---|---|
| `long_th/` | long_th |
| `vy_th/` | vy_th |
| `truyen_lp/` | truyen_lp |
| `nhat_npm/` | nhat_npm |
| `nhat_dm/` | nhat_dm |
| `han_htg/` | han_htg |
| `dieu_sp/` | dieu_sp |

## How to start

```bash
git checkout main && git pull origin main
git checkout -b feat/lab05-practice-<member>
cp <lab_materials>/lab05/practice/{make_school_db.py,check.py,test_school_repo.py,school_repo.py,my_answers.sql} submissions/lab05/<member>/
cd submissions/lab05/<member>
python make_school_db.py      # creates school.db (git-ignored)
python check.py               # Q1–Q15 score
pytest -q test_school_repo.py # D1–D3
```

Do not edit `check.py` or the test file. Do not commit `school.db`.
