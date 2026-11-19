# Lab 6 — individual submissions

One folder per member, already created with templates. **Each PR may change only your own folder.**
Full rules and the team part: `docs/team-plan-lab06.md`.

| Folder | Member | H1 ids |
|---|---|---|
| `long_th/` | Member 1 (Tech Lead) | E21–E25 |
| `vy_th/` | Member 2 | E26–E30 |
| `truyen_lp/` | Member 3 | E31–E35 |
| `nhat_npm/` | Member 4 | E36–E40 |
| `nhat_dm/` | Member 5 | E41–E45 |
| `han_htg/` | Member 6 | E46–E50 |
| `dieu_sp/` | Member 7 | E51–E55 |

`_practice/` holds the original `mini_search.py` and `test_mini_search.py` (the checker compares your test file to it).

## How to start

```bash
git checkout main && git pull origin main
git checkout -b lab6/<member>
pip install -e .                     # once, from the repo root (inside your .venv)
```

## What goes where

| Task | File in `submissions/lab06/<member>/` | Run (from the repo root unless noted) |
|---|---|---|
| T1 S1–S3 mini search | `mini_search.py` | `cd submissions/lab06/<member> && pytest -q test_mini_search.py` → `4 passed` |
| T2 A2 / T3 A1 | team code: `assistant_core/llm.py` (`parse_draft`), `assistant_core/rag/answerer.py` | `pytest -q tests/test_rag.py -k citation` / `-k abstain` |
| T4 comparison | `path_comparison.md` (table + 3 sentences) | `python eval/compare_paths.py` |
| T5 H1 5 cases | `h1_cases.jsonl` + re-run table in `path_comparison.md` | `python eval/compare_paths.py --cases eval/cases.jsonl submissions/lab06/<member>/h1_cases.jsonl` |
| T6 reflection | `reflection.md` (5 lines between the markers) | — |
| T7 bonus | `bonus.md` | Ollama: `LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python eval/compare_paths.py` |

Chunk ids for `expect_source` are the `## <id>` headings in `assistant_core/data/kb/*.md` (e.g. `S26#1`, `H26#5`).

## Before you send the PR link

```bash
python submissions/lab06/check.py <member>
```

It must end with every required line `[PASS]` (exit code 0). Paste its last line into your folder's `README.md`.
Do not edit `test_mini_search.py`. Never commit `.env`, `.venv/` or `*.db`.
