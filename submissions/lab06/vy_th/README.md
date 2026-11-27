# Lab 6 — vy_th

Individual submission. Rules: `docs/team-plan-lab06.md`.

- Branch: `lab6/vy_th`
- H1 IDs: E26–E30 (Member 2)
- Issue: #55
- Reviewer: `truyen_lp`

## Checklist

- [x] **T1** `mini_search.py` — S1–S3 completed; all 4 tests passed.
- [x] **T2/T3** A2 grounding check and A1 abstain — studied the existing implementation and verified the tests.
- [x] **T4** `path_comparison.md` — baseline evaluation output and three sentences.
- [x] **T5** `h1_cases.jsonl` — five additional evaluation cases with valid IDs and sources, updated comparison table and explanation.
- [x] **T6** `reflection.md` — five-line reflection explaining RAG.
- [x] **T7** `bonus.md` — Ollama experiment and comparison with StubLLM.
- [x] No `.env`, `.venv/`, `*.db` or API key committed.

## Test results

| Test | Result |
|---|---|
| Starter test suite | 42 passed, 1 warning |
| Mini Search | 4/4 passed |
| A1/A2 | 2 passed, 13 deselected |
| Individual self-check | All required checks passed |
| Bonus | Completed |

`python submissions/lab06/check.py vy_th`:

```
Individual points found by this script: 7/6  (+ A1/A2 4 pts in lab06/starter, + bonus)
```

## Evaluation summary

| Path | Base cases | With H1 cases |
|---|---:|---:|
| Deterministic | 7/20 | 9/25 |
| Retrieval | 16/20 | 21/25 |
| LLM (stub) | 16/20 | 21/25 |

All five additional H1 cases passed on both retrieval and LLM paths.

## Bonus — Ollama

Llama 3.2 achieved 17/20 on the base evaluation, compared with 16/20 for StubLLM. E14 improved, but E19 remained unresolved. The real model also required considerably more processing time.

Further details are available in `bonus.md`.

## AI use

- **Tool:** ChatGPT (OpenAI)
- **Date:** 2026-11-20
- **Purpose:** Used AI as a learning assistant throughout Lab 06.
- **How I used AI:** Received step-by-step explanations of inverted indexes, dictionaries, sets, search scoring, sorting, grounding checks, and abstention. Used AI assistance to interpret evaluation results, formulate H1 test questions, draft the comparison analysis and H2 reflection, and configure Ollama on macOS.
- **What I kept:** The provided starter implementation, original test files, evaluation framework, and individual submission structure.
- **What I changed:** Implemented S1–S3, added five H1 evaluation cases, completed the comparison and reflection documents, and recorded the Ollama experiment results.
- **Verification:** Executed the tests, baseline evaluation, H1 evaluation, Ollama experiment, and individual self-check locally. All required self-checks passed.
- **Shared AI usage log:** To be recorded separately in `docs/ai-use-log.md` to respect the individual PR scope.
