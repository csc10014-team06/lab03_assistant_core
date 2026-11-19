# Lab 6 — Team plan: RAG, abstain, grounding, eval

Sources: *Lab 6 – Task description & hướng dẫn cho nhóm* (Nov 19, 2026) and the official Lab 6 materials from the
`lab_materials` branch, now in `lab06/` (`practice/`, `starter/`, `worksheets/`).

## 1. Where everything lives

| Work | Who | Where in this repo | Points |
|---|---|---|---|
| **T1** S1–S3 mini search | every member | `submissions/lab06/<member>/mini_search.py` (copy of `lab06/practice/`) | 2 |
| **T2** A2 grounding check | every member explains; one version merged | `lab06/starter/src/assistant_core/llm.py` → `parse_draft` | 2 |
| **T3** A1 abstain | every member explains; one version merged | `lab06/starter/src/assistant_core/rag/answerer.py` | 2 |
| **T4** comparison output + 3 sentences | every member | `submissions/lab06/<member>/path_comparison.md` | 1 |
| **T5** H1 5 cases + re-run + 1 sentence | every member | `submissions/lab06/<member>/h1_cases.jsonl` (+ `path_comparison.md`) | 2 |
| **T6** H2 reflection, 5 lines | every member | `submissions/lab06/<member>/reflection.md` | 1 |
| **T7** bonus: Ollama **or** H3 | optional | `submissions/lab06/<member>/bonus.md` (H3 code: one team PR) | +1 |
| Merge, re-run, tag **`v0.6-ai`** | Tech Lead (long_th) | `main` | — |

`lab06/starter/` is the Lab 6 app. It is self-contained (its own `src/assistant_core`, data, tests and eval), like the
starters of earlier labs. It is **not** wired into our root `assistant_core` package. The root package and its CI are
unchanged by Lab 6.

## 2. What was added to the official materials to make them run

| Change | Why |
|---|---|
| **A1** filled in `rag/answerer.py`, exactly the 2 lines from the task sheet | without it every handbook question raises `NotImplementedError` and `compare_paths.py` crashes |
| **A2** filled in `llm.py` (`parse_draft`), exactly the 2 lines from the task sheet | without it `test_citation_of_unretrieved_source_is_rejected` fails (40/42) |
| `eval/compare_paths.py`: optional extra case files, `--include-submissions`, `--min-correct N`, case validation (unknown chunk id, duplicate id), and it now runs from any directory | lets each member keep H1 cases in their own folder (no merge conflicts), gives CI a gate, and fixes the "cannot find `eval/cases.jsonl`" error from the sheet's common-errors table. The output for the base 20 cases is unchanged. |
| CI job `lab06-starter`: `ruff`, `pytest -q` (42), eval gate ≥ 16/20 | the starter is now checked on every push and PR |
| root `pyproject.toml`: `lab06/practice` excluded from ruff | the warm-up ships with TODOs (unused variables) |

With A1/A2 in place: `pytest -q` → **42 passed**; `compare_paths.py` → deterministic 7/20, **retrieval 16/20, llm
(stub) 16/20**, failing E13, E14, E15, E19 as the sheet expects. Analysis: `docs/lab6/path_comparison.md`.

A1/A2 are already on `main` (the task sheet gives the exact code), so the app runs for everyone. Each member should
still be able to explain both checks (T6 asks for that). If the professor wants to see each member type them, revert the
two `if` blocks on your own branch, type them again, and show `pytest -q tests/test_rag.py -k "citation or abstain"` go
from red to green.

## 3. Commands (task sheet → this repo)

All starter commands run in `lab06/starter`, in **its own** `.venv`. The root `.venv` also has an `assistant_core`, and
the two packages have the same name.

```bash
cd lab06/starter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env                    # keep RETRIEVAL_MIN_SCORE=2.0
pytest -q                               # 42 passed
python -m assistant_core "I lost my student card"          # ... source: S26#3
python -m assistant_core "what is the capital of France"   # apology + Training Office
python eval/compare_paths.py
python eval/compare_paths.py ../../submissions/lab06/<member>/h1_cases.jsonl   # T5
python eval/compare_paths.py --include-submissions                              # everyone's H1
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python eval/compare_paths.py             # T7 Ollama
```

Practice (T1): `cd submissions/lab06/<member> && pytest -q test_mini_search.py` → `4 passed`.
Self-check: `python submissions/lab06/check.py <member>` (from the repo root, any venv with the requirements).

## 4. Rules for the individual PRs

1. Branch from `main`: `lab6/<member>` (e.g. `lab6/vy_th`). CI runs on `lab6/**`.
2. The PR may change **only** `submissions/lab06/<member>/`. Code changes (H3, KB fixes) go through a team PR.
3. PR title: `Lab 6 – <member> – A1/A2 + comparison`. Description: paste the output of
   `python submissions/lab06/check.py <member>`.
4. H1 ids must be in your range (table in `submissions/lab06/README.md`). `expect_source` must be a real chunk id such
   as `S26#1`, `F26#3` or `H26#5.3`; `compare_paths.py` and the checker reject anything else.
5. Draft PR at the end of the session; final deadline for H1/H2/bonus **23:59 the day before Lab 7**.
6. AI use goes into `docs/ai-use-log.md` as usual.

**Open question for thầy Tùng / the TA:** H1 per person, or merged into one file? We support both. Each member's cases
stay in their own `h1_cases.jsonl`, and `--include-submissions` evaluates them together. If merging is required, the
Tech Lead appends them to `lab06/starter/eval/cases.jsonl` once all PRs are in. The ids cannot collide.

The worksheets in `lab06/worksheets/` (`path_comparison.md`, `difficult_queries.md`) are the professor's generic
versions. Our task sheet's T4/T5 replace them; fill them in only if the TA asks for them.

## 5. Checklist for the Tech Lead before tagging `v0.6-ai`

- [ ] `python submissions/lab06/check.py --all` → every member ✅ on T1, T4, T5, T6, hygiene
- [ ] Merge at most one H3 PR (if any); re-run the eval and raise `--min-correct` in CI if retrieval improves
- [ ] CI green on `main` (root `test` job and `lab06-starter` job)
- [ ] `cd lab06/starter && python eval/compare_paths.py --include-submissions` pasted into `docs/lab6/path_comparison.md`
- [ ] No `.env` / `*.db` in `git ls-files`
- [ ] `git checkout main && git pull && git tag v0.6-ai && git push origin v0.6-ai`, then post the tag link on the LMS
