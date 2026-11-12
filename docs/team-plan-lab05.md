# Lab 5 — Team plan: submission design (data, SQL, persistence)

Source: `CSC10014_2026_Lab05_Data_SQL_Persistence_Tutorial` (PDF). The Lab 5 starter/practice files were **not yet in
`lab_materials`** when this was written (only `lab01`–`lab04`), so file and function names below come from the
tutorial text. Re-check them against `lab05/practice/` and `lab05/starter/` once the professor publishes them.

## 1. Two kinds of submission

Lab 5 mixes **individual** work (every member does it) and **team** work (the assistant). They live in different places.

| Work | Who | Where in this repo | Graded by (points) |
|---|---|---|---|
| SQL practice **Q1–Q15** on `school.db` | every member | `submissions/lab05/<member>/my_answers.sql` | `check.py` score: Q1–Q10 = 3, Q11–Q15 = 2 |
| Python practice **D1–D3** (`school_repo.py`, incl. the injection test) | every member | `submissions/lab05/<member>/school_repo.py` | `pytest` green = 2 |
| **H1** reach 15/15, **H2** one extra question + query + result | every member | `submissions/lab05/<member>/` (`my_answers.sql`, `h2.md`) | H2 or F1–F3 = 1 |
| **R1–R2** feedback saved in SQLite, survives a restart | team | `assistant_api/` (`db.py`, `main.py`) + `tests/` | tests green + restart = 2 |
| **F1–F3** queries on the assistant data | team | `sql/my_queries.sql` | (with H2) |
| Data-model design review (**H3**, bonus) | team | `docs/lab5/data_model.md` | +1 |
| Tag **`v0.5-data`** | Tech Lead (long_th) | git tag on `main` | link on the LMS |

Why a folder per member: seven people submit the same file names (`my_answers.sql`, `school_repo.py`). Separate
folders mean **no merge conflicts**, every PR touches only its own folder, and each member still has their own PR link
for the LMS ("PR link on the LMS").

## 2. Layout

```
submissions/lab05/
  README.md                 # rules (below), read once
  <member>/                 # long_th, vy_th, truyen_lp, nhat_npm, nhat_dm, han_htg, dieu_sp
    README.md               # checklist + pasted results (already created, fill it in)
    make_school_db.py       # copied from lab05/practice (unchanged)
    check.py                # copied unchanged
    test_school_repo.py     # copied unchanged
    school_repo.py          # YOUR D1–D3
    my_answers.sql          # YOUR Q1–Q15
    h2.md                   # YOUR H2: question, query, pasted result
assistant_api/db.py         # team: SQLModel tables + Repository (from the starter, adapted)
sql/migrations/001_init.sql, 002_add_faq.sql      # team: from the starter
sql/my_queries.sql          # team: F1–F3 (+ H2)
scripts/migrate.py, scripts/seed.py               # team: from the starter
docs/lab5/data_model.md     # team: bonus H3
```

- **Never commit** `school.db`, `assistant.db` or `.env`. `*.db` is now in `.gitignore`. The seed/migrate scripts
  recreate the files in seconds. The hashing **salt** goes in `.env` only (`.env.example` holds a placeholder).
- `submissions/` is excluded from `ruff` and not collected by CI's `pytest` (`testpaths = ["tests"]`); practice code
  would otherwise turn CI red for reasons unrelated to the assistant. Run the practice checks **inside your folder**:
  `python make_school_db.py && python check.py && pytest -q test_school_repo.py`.
- Only copy the practice files you need. Do not edit `check.py` or the tests.

## 3. Rules for the individual PRs

1. Branch from `main`: `feat/lab05-practice-<member>` (e.g. `feat/lab05-practice-vy_th`). CI runs on `feat/**`.
2. The PR may change **only** `submissions/lab05/<member>/`. Anything else goes through a team PR.
3. PR description: paste the last lines of `check.py` (`Score: n/15`) and of `pytest -q` (`5 passed`).
4. Submit the PR link on the LMS. Draft PRs are accepted at the end of the session; final deadline **23:59 the day
   before Lab 6** for H1/H2.
5. Review at least one other member's practice PR (suggested pairs as in Lab 4).
6. AI use goes into `docs/ai-use-log.md` as usual.

## 4. Team work (the assistant) — proposed split

The tutorial's R1/R2 are small; the real work is wiring a database into **our** package (as in Lab 4, the starter has
its own `assistant_core`, so copy only what fits ours).

| Owner | Work | Done when |
|---|---|---|
| **han_htg** | Foundation: bring in `assistant_api/db.py`, `sql/migrations/`, `scripts/migrate.py`, `scripts/seed.py` from the Lab 5 starter, adapted to our flat layout; README "Database" section | `python scripts/migrate.py assistant.db` runs twice safely; tables `chat_session`, `interaction`, `feedback` exist |
| **long_th** | Settings: DB location + hashing salt (`ASSISTANT_DB_URL`, `ASSISTANT_HASH_SALT`, salt hidden from `repr()`), add `sqlmodel` to `requirements.txt` / `pyproject.toml`, `.env.example`; **integration** + tag `v0.5-data` | config tests; `pytest` + `ruff` green on `main`; tag pushed |
| **dieu_sp** | **R1** `add_feedback` (404 for an unknown `request_id`) and **R2** `list_feedback` (newest first, limit 100) in `Repository`; replace `feedback_store` in `assistant_api/main.py` | feedback tests green |
| **vy_th** | Record every `/v1/chat` answer with `record_interaction` (hashed session, intent, topic = rule id, resolved, degraded, latency_ms; **no message text**) | a chat creates one `interaction` row |
| **nhat_dm** | Persistence tests: feedback survives restarting the app against the same DB file; unknown id → 404; duplicate `request_id` handling | restart test green |
| **truyen_lp** | `sql/my_queries.sql` F1–F3 (per intent, avg latency, most thumbs-down topics) on seeded data | queries run; sample output pasted in the PR |
| **nhat_npm** | Privacy review + `docs/lab5/data_model.md` (what we do **not** store and why; the 3 problems of `sql/bad_schema.sql`) | no raw text / names / salt in the DB or in Git |

Merge order: han_htg + long_th first (small, same day) → dieu_sp / vy_th → nhat_dm / truyen_lp / nhat_npm →
integration, tag `v0.5-data`.

## 5. Things that will bite (found while reading our current code)

- **Existing test must change.** `tests/test_api.py::test_feedback_roundtrip` posts feedback for `"abc123"`, an id no
  chat ever produced. After R1, that is a **404**. Update it to call `/v1/chat` first and use the returned
  `request_id`; add a separate test for the 404. (`test_api.py` is a Lab 4 file; the "do not touch" rule only covers the
  Week 3 tests.)
- **Where `topic` comes from.** Our `respond()` returns `sources=[Source(id, title)]`; use `sources[0].id` as the
  `topic` for rule answers and `None` otherwise. `resolved` should be `False` when the intent is `unknown`.
- **Latency** has to be measured around `service.respond()` in `chat()`.
- **Tests must use an in-memory or temp-dir database** (never the real `assistant.db`), like the tutorial's
  `sqlite3.connect(":memory:")` for `school_repo`.
- **SQLModel is a new dependency**; pin it in `requirements.txt` and give `pyproject.toml` a range, as we did for
  FastAPI.
- `v0.4-api` is **not tagged on GitHub yet** (no tags in the remote). Tag it before Lab 5 work lands on `main`.

## 6. Checklist for the Tech Lead before tagging `v0.5-data`

- [ ] 7 member folders exist, each with `Score: 15/15` and `5 passed` pasted in its README
- [ ] `pytest` and `ruff check .` green on `main`; no `*.db` / `.env` in `git ls-files`
- [ ] Start the API, send chat + feedback, stop, start again, list feedback with the admin key: the row is still there
- [ ] `sql/my_queries.sql` runs on a freshly seeded `assistant.db`
- [ ] `git tag v0.5-data && git push origin v0.5-data`, then post the tag link on the LMS
