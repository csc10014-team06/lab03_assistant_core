# Lab 7 — individual submissions

One folder per member, already created with the practice files and both worksheets. **Each PR may change only your
own folder.** Rules: `docs/team-plan-lab07.md`.

| Folder | Member |
|---|---|
| `long_th/` | long_th (Tech Lead) |
| `vy_th/` | vy_th |
| `truyen_lp/` | truyen_lp |
| `nhat_npm/` | nhat_npm |
| `nhat_dm/` | nhat_dm |
| `han_htg/` | han_htg |
| `dieu_sp/` | dieu_sp |

## Steps

```bash
git checkout main && git pull origin main
git checkout -b lab7/<member>
cd lab07/starter && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e . && cp .env.example .env
```

1. **T1:** do U2–U4 in `submissions/lab07/<member>/hello_streamlit.py`, then run `pytest -q test_hello_streamlit.py` → 4 passed.
2. **T2:** start the API and the UI (`docs/team-plan-lab07.md` §3), then go through `usability_checklist.md`.
   Tick what works; for anything that doesn't, leave it unticked and write why after ` — `.
3. **T3:** give someone outside the team the task in `user_test_observations.md`. Watch them without helping, and fill in
   at least 3 rows. First name only.
4. From the repo root, with the Lab 7 venv active: `python submissions/lab07/check.py <member>`. Every line must say
   `[PASS]`.
