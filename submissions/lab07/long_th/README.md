# Lab 7 — long_th

Individual submission. Change **only this folder** in your PR. Rules: `docs/team-plan-lab07.md`.
Branch `lab7/long_th` · PR title `Lab 7 – long_th – UI + user test`.

## Tasks (`python submissions/lab07/check.py long_th` checks them)
- [x] **T1** `hello_streamlit.py` — U2–U4 TODOs done; `pytest -q test_hello_streamlit.py` → `4 passed` (do not edit the test)
- [x] **T2** Run the app (API + `streamlit run ui/app.py` in `lab07/starter`), go through `usability_checklist.md`:
      tick each item that works; for an item that does not, leave it unticked and write why after ` — `
- [ ] **T3** 10-minute user test with someone **outside the team** → `user_test_observations.md`: tester first name, date,
      at least 3 rows (what they did, what they expected, why, fix idea). Do not help them during the test
- [x] No `.env`, `.venv/` or screenshots with personal data committed

## Results (paste the real output)

`pytest -q test_hello_streamlit.py`:

```
4 passed in 0.30s
```

**T2 — how each item was checked:** the API and `streamlit run ui/app.py` ran locally and the page was driven in
Chromium (Playwright) at 1280 px and at 375 px (phone). "Thinking…" was checked against a backend that answers after
3 s, because the offline stub is too fast to see it. The contrast was measured from the page's computed colours. Two
items are not ticked (phone: no AI notice on the first screen; grey "Sources" caption below 4.5:1 and emoji-only
👍/👎 buttons) — both are candidates for the team's one UI fix (#81).

**T3 — still to do (needs a real person, ~10 min).**
1. Start the API and the UI (`docs/team-plan-lab07.md` §3). Ask someone **outside the team**; write down their first
   name only.
2. Give them exactly the task at the top of `user_test_observations.md`. Do not help or explain; say only "please
   think aloud".
3. Note every hesitation, wrong click or surprise in a row: what they did/said, what they expected, why the UI caused
   it, a fix idea. Watch especially: do they find the example questions (sidebar), do they notice the sources, do they
   see 👍/👎.
4. Fill in at least 3 rows, then `python submissions/lab07/check.py long_th` → T3 `[PASS]`.

## AI use
- **Tool:** Claude Code, at my request. It wrote U2–U4 in `hello_streamlit.py`, ran the usability checks above
  (browser automation, contrast measurement) and wrote `usability_checklist.md` from what it measured.
- **Not done by AI:** the T3 user test — it needs a real tester and real observations.
