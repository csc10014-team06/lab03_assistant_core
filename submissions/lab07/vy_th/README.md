# Lab 7 — vy_th

Individual submission. Rules: `docs/team-plan-lab07.md`.

Branch `lab7/vy_th` · PR title `Lab 7 – vy_th – UI + user test`.

## Tasks

- [x] **T1** — Completed Streamlit warm-up exercises U2–U4.
- [x] **T2** — Completed the usability checklist: 9/10 ticked, with the remaining item explained.
- [x] **T3/H1** — Conducted a usability test with someone outside the team and documented three observations.
- [x] **H2** — Completed the Google PAIR Guidebook reflection in `h2_reflection.md`.
- [x] No `.env`, `.venv/`, database files, or screenshots containing personal data committed.
- [x] AI usage documented in `docs/ai-use-log.md`.
- [ ] Team UI fix commit link and before/after screenshots.

## Results

`pytest -q test_hello_streamlit.py`:

```
4 passed
```

Lab 7 starter tests:

```
49 passed, 1 warning
```

`python submissions/lab07/check.py vy_th`:

```
Lab 7 — vy_th

[PASS] T1 Streamlit practice    4/4 passed
[PASS] T2 usability checklist  9/10 ticked, the rest explained
[PASS] T3 user test             3 observations
[PASS] hygiene                  no .env / .venv / *.db
```

## Usability findings

1. The assistant returned the replacement location instead of the required documents for replacing a lost student card.
2. The assistant did not provide the requested replacement fee or acknowledge the missing information.
3. Source references did not include clickable links to the original documents.

## AI use

Logged in `docs/ai-use-log.md`: yes.

Tool: ChatGPT (OpenAI).

## Pending

Awaiting the shared team UI fix, its commit link, and before/after screenshots.
