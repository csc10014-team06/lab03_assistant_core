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

`mini_search.py` and `test_mini_search.py` in your folder are copies of `lab06/practice/` (the checker compares
your test file to the original).

## How to start

```bash
git checkout main && git pull origin main
git checkout -b lab6/<member>
cd lab06/starter
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env
pytest -q                                              # 42 passed
```

Use this separate `.venv` for the starter: it has its own `assistant_core` package, different from the one at the repo
root.

## What goes where

| Task | File in `submissions/lab06/<member>/` | Run |
|---|---|---|
| T1 S1–S3 mini search | `mini_search.py` | `cd submissions/lab06/<member> && pytest -q test_mini_search.py` → `4 passed` |
| T2 A2 / T3 A1 | already in `lab06/starter/src/assistant_core/llm.py` (`parse_draft`) and `rag/answerer.py` | `cd lab06/starter && pytest -q tests/test_rag.py -k "citation or abstain"` |
| T4 comparison | `path_comparison.md` (output + 3 sentences) | `cd lab06/starter && python eval/compare_paths.py` |
| T5 H1 5 cases | `h1_cases.jsonl` + re-run output in `path_comparison.md` | `cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/<member>/h1_cases.jsonl` |
| T6 reflection | `reflection.md` (5 lines between the markers) | — |
| T7 bonus | `bonus.md` | `cd lab06/starter && LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python eval/compare_paths.py` |

Chunk ids for `expect_source` are `<doc_id>#<heading number>` from `lab06/starter/data/kb/*.md`:
`H26#4.2` … `H26#8.3` (handbook), `F26#1` … `F26#4` (fees), `S26#1` … `S26#3` (services).
`compare_paths.py` rejects unknown chunk ids and duplicate case ids.

Put your 5 cases in **your** `h1_cases.jsonl`, not in `lab06/starter/eval/cases.jsonl`. Seven PRs appending to the
same file would conflict. `python eval/compare_paths.py --include-submissions` evaluates everyone's cases together.

## Before you send the PR link

```bash
python submissions/lab06/check.py <member>
```

Every required line must say `[PASS]` (exit code 0). Paste the script's last line into your folder's `README.md`.
Do not edit `test_mini_search.py`. Never commit `.env`, `.venv/` or `*.db`.
