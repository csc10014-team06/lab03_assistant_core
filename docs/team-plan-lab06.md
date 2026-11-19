# Lab 6 — Team plan: RAG, abstain, grounding, eval

Source: *Lab 6 – Task description & hướng dẫn cho nhóm* (Nov 19, 2026). The official `lab06/practice/` and
`lab06/starter/` archives were **not in the repo** when this was set up, so the practice file, the knowledge base,
the 20 eval cases and the RAG code were written to match the task text (same function names, same TODO code, same
expected results: `[('D3', 3)]`, source `S26#3`, retrieval ≈ 16/20 with E13/E14/E15/E19 failing). If the professor's
starter differs, diff it against the files listed in §2 and adapt.

## 1. Two kinds of submission

| Work | Who | Where in this repo | Points |
|---|---|---|---|
| **T1** S1–S3 mini search | every member | `submissions/lab06/<member>/mini_search.py` | 2 |
| **T2** A2 grounding check | every member reads/explains; one version merged | `assistant_core/llm.py` → `parse_draft` | 2 |
| **T3** A1 abstain | every member reads/explains; one version merged | `assistant_core/rag/answerer.py` → `RagAnswerer.answer` | 2 |
| **T4** comparison table + 3 sentences | every member | `submissions/lab06/<member>/path_comparison.md` | 1 |
| **T5** H1 5 cases + re-run + 1 sentence | every member | `submissions/lab06/<member>/h1_cases.jsonl` (+ `path_comparison.md`) | 2 |
| **T6** H2 reflection, 5 lines | every member | `submissions/lab06/<member>/reflection.md` | 1 |
| **T7** bonus: Ollama **or** H3 | optional | `submissions/lab06/<member>/bonus.md` (H3 code: one team PR) | +1 |
| Merge, re-run, tag **`v0.6-ai`** | Tech Lead (long_th) | `main` | — |

A1 and A2 are already in `main` (the exact code from the task sheet), so `python -m assistant_core` works for
everyone and CI stays green. For the individual PR, each member should be able to point at both checks and explain
them (T6 asks for that too). If the professor wants to see A1/A2 typed by each member, revert the two `if` blocks on
your branch, re-type them, and show `pytest -q tests/test_rag.py -k "citation or abstain"` going from red to green.

## 2. Layout (task sheet path → our path)

Our package is flat (`assistant_core/`, no `src/`), and the commands run from the **repo root** (the sheet says `starter/`).

| Task sheet | This repo |
|---|---|
| `lab06/practice/mini_search.py` | `submissions/lab06/<member>/mini_search.py` (original in `submissions/lab06/_practice/`) |
| `src/assistant_core/llm.py` (`parse_draft`, `TODO A2`) | `assistant_core/llm.py` |
| `src/assistant_core/rag/answerer.py` (`TODO A1`) | `assistant_core/rag/answerer.py` |
| `src/assistant_core/rag/index.py` (`tokenize`, H3) | `assistant_core/rag/index.py` |
| `data/kb/` | `assistant_core/data/kb/H26.md` (academic rules), `S26.md` (student services) — 18 chunks |
| `eval/cases.jsonl`, `eval/compare_paths.py` | `eval/cases.jsonl`, `eval/compare_paths.py` (metrics in `assistant_core/evaluation.py`) |
| `docs/lab6/path_comparison.md` | team baseline: `docs/lab6/path_comparison.md`; yours: `submissions/lab06/<member>/path_comparison.md` |
| `tests/test_rag.py` | `tests/test_rag.py` (+ `tests/test_eval.py`, `tests/test_lab06_check.py`) |
| `pytest -q` → `42 passed` | our suite is bigger (Lab 3–6): **`381 passed`** on `main` |
| `RETRIEVAL_MIN_SCORE=2.0` in `.env` | `ASSISTANT_RETRIEVAL_MIN_SCORE` (the unprefixed name from the sheet also works); default 2.0 — do not change |

## 3. How the three paths work

```
question ──► rules      keyword rules (Lab 3 handle()/respond(), unchanged; kept on purpose — do not delete)
         └─► retrieval  KBIndex.search → A1: top score < min_score? → "Sorry … Training Office" (no model call)
                                        └► answer = best chunk text, source = its id
         └─► llm        same search + A1 → draft provider (stub | ollama) → parse_draft + A2 grounding check
                                        └► reject → escalate (degraded=True) · ok → answer + cited ids
```

* CLI: `python -m assistant_core "I lost my student card"` uses `ASSISTANT_ANSWER_PATH` (default `llm`);
  `--path rules|retrieval|llm` overrides it. Greetings, fees and office look-ups stay on the rules in every path
  (they compute or look up structured data). The HTTP API (`/v1/chat`) still uses the rules path.
* Eval: `compare_paths.py` measures each path **on its own** (no fee/office routing), so the numbers compare approaches.

## 4. Eval metrics

`python eval/compare_paths.py [--include-submissions] [--out FILE.md] [--json FILE.json] [--min-pass PATH=N]`

Per path: passed / accuracy, right source on answerable questions, correct abstains, false abstains, wrong sources,
grounding rejections, mean latency (ms), the failing ids, and a per-case ✅/❌ matrix. Baseline (stub):
**rules 9/20 · retrieval 16/20 · llm (stub) 16/20**; analysis in `docs/lab6/path_comparison.md`.
CI runs it with `--min-pass retrieval=16 --min-pass llm=16`: a change that makes retrieval worse fails the build.
(If someone merges H3, E14 passes → 17/20; raise the gate then.)

## 5. Rules for the individual PRs

1. Branch from `main`: `lab6/<member>` (e.g. `lab6/vy_th`). CI runs on `lab6/**`.
2. The PR may change **only** `submissions/lab06/<member>/`. Code changes (H3, KB fixes) go through a team PR.
3. PR title: `Lab 6 – <member> – A1/A2 + comparison`. Description: paste the output of
   `python submissions/lab06/check.py <member>`.
4. H1 ids must be in your range (table in `submissions/lab06/README.md`); `expect_source` must be a real chunk id —
   the checker rejects anything else.
5. Draft PR at the end of the session; final deadline for H1/H2/bonus **23:59 the day before Lab 7**.
6. AI use goes into `docs/ai-use-log.md` as usual.

**Open question for thầy Tùng / the TA:** H1 per person or merged into one file? We support both: each member's
cases stay in their own `h1_cases.jsonl`; `--include-submissions` evaluates them all together. If merging is
required, the Tech Lead appends them to `eval/cases.jsonl` (ids cannot collide).

## 6. Checklist for the Tech Lead before tagging `v0.6-ai`

- [ ] `python submissions/lab06/check.py --all` → every member ✅ on T1, T4, T5, T6, hygiene
- [ ] Pick at most one H3 PR to merge (if any); re-run the eval and update the CI gate
- [ ] `pytest -q` and `ruff check .` green on `main`
- [ ] `python eval/compare_paths.py --include-submissions --out docs/lab6/path_comparison_all.md` committed
- [ ] `python -m assistant_core "I lost my student card"` → answer with `(source: S26#3)`;
      `python -m assistant_core "what is the capital of France"` → apology + Training Office
- [ ] No `.env` / `*.db` in `git ls-files`
- [ ] `git checkout main && git pull && git tag v0.6-ai && git push origin v0.6-ai`, then post the tag link on the LMS
