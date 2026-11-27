# Lab 7 — Team plan: user interface + usability test

Source: the Lab 7 materials from the `lab_materials` branch, now in `lab07/` (`practice/`, `starter/`, `worksheets/`).
**No Lab 7 task sheet was available when this was written**, so there are no point values or exact deadlines below.
Check them against the sheet once the professor publishes it, and update this file and the issues.

## 1. Tasks

| Task | Who | Where | Done when |
|---|---|---|---|
| **T1** Streamlit warm-up U2–U4 | every member | `submissions/lab07/<member>/hello_streamlit.py` | `pytest -q test_hello_streamlit.py` → 4 passed |
| **T2** Usability checklist on the running app | every member | `submissions/lab07/<member>/usability_checklist.md` | every item ticked, or unticked with the reason after ` — ` |
| **T3** 10-minute user test with someone outside the team | every member | `submissions/lab07/<member>/user_test_observations.md` | tester first name + date, ≥ 3 complete observation rows |
| **Team** one UI fix from the user tests, merge, tag | Tech Lead (long_th) | `lab07/starter/ui/` | fix merged, its commit linked in the worksheets, tag pushed |

`python submissions/lab07/check.py <member>` checks T1–T3. Run it with the Lab 7 venv, because T1 needs Streamlit.

## 2. What was added to the materials to make them run

| Change | Why |
|---|---|
| **L1** `format_sources` and **L2** `status_note` in `ui/logic.py`, exactly as the TODO hints describe | both raised `NotImplementedError`, so `tests/test_ui.py` failed (47/49) and the UI crashed on the first answer |
| **F1** the 👎 button in `ui/app.py` (rating −1, remembered, toast) | the checklist item "each answer has 👍 / 👎" could not pass without it |
| CI job `lab07-starter`: ruff, `pytest -q` (49), eval check ≥ 16/20; CI also runs on `lab7/**` | the starter is checked on every push and PR |

The long TODO comment that failed ruff (E501) went away with L2. With these changes: `pytest -q` → **49 passed**.
Clicked through the real UI against a running API: the answer shows `Sources: S26#3 — …`, 👎 shows the toast and stores
a rating −1 row, an out-of-scope question shows the Training Office note, and a stopped backend shows the "not reachable" error.

As in Lab 6, these TODOs are filled on `main` so the app runs for everyone. If the professor wants each member to write
L1/L2/F1, revert them on your own branch and show `pytest -q tests/test_ui.py` going from red to green.

## 3. Commands

```bash
cd lab07/starter
python -m venv .venv && source .venv/bin/activate      # its own venv (its own assistant_core, + streamlit)
pip install -r requirements.txt && pip install -e .
cp .env.example .env
pytest -q                                              # 49 passed
uvicorn assistant_api.main:create_app --factory        # terminal 1: the API on :8000
streamlit run ui/app.py                                # terminal 2: the UI on http://localhost:8501
```

T1: `cd submissions/lab07/<member> && pytest -q test_hello_streamlit.py` (same venv).
Run the app with `streamlit run hello_streamlit.py` to see your practice page.

## 4. Rules for the individual PRs

1. Branch from `main`: `lab7/<member>`. CI runs on `lab7/**`.
2. The PR may change **only** `submissions/lab07/<member>/`. The UI fix goes through one team PR.
3. PR title: `Lab 7 – <member> – UI + user test`. Paste `python submissions/lab07/check.py <member>` in the description.
4. **User test privacy:** first name only, no photos of the tester, no screenshots that show personal data.
5. AI use goes into `docs/ai-use-log.md` as usual.

## 5. Checklist for the Tech Lead

- [ ] Get the Lab 7 task sheet: points, deadlines, tag name, and whether the user test is per member or per team
- [ ] Collect the fix ideas from everyone's `user_test_observations.md`, pick **one**, implement it in one team PR, and
      ask members to paste its commit link into "The one change we made"
- [ ] `python submissions/lab07/check.py --all` (Lab 7 venv) → every member ✅
- [ ] CI green on `main` (`test`, `lab06-starter`, `lab07-starter`)
- [ ] Tag `main` with the name from the sheet (e.g. `v0.7-ui`) and post the link on the LMS
