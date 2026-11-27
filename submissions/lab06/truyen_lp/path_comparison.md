# Lab 6 — Path comparison (truyen_lp)

## T4 — base 20 cases

<!-- cd lab06/starter && python eval/compare_paths.py   — paste everything it prints between the fences. -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.3   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.0   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.1     0.3   fails: E13 E14 E15 E19
```

### 3 sentences (exactly one per line, replace TODO)

(a) For handbook questions I would use: the `llm` path (with `retrieval` as its automatic degraded fallback).
(b) Because: it reaches 16/20 accuracy (compared to 7/20 for `deterministic`), phrases answers cleanly from retrieved chunks, enforces `min_score` abstention and citation grounding checks, and safely quotes the top source if the model fails.
(c) The failure I would fix first (one of E13, E14, E15, E19): I would fix E13 ("when is tuition due") and E15 ("how long can I keep a library book") first by refining the deterministic router so policy questions containing "tuition" or "library" are not hijacked by the fee or office tools before retrieval can run.

## T5 — with my 5 H1 cases (E31–E35)

<!-- cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/truyen_lp/h1_cases.jsonl -->

```
cases: 25 from lab06\starter\eval\cases.jsonl, submissions\lab06\truyen_lp\h1_cases.jsonl
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.3   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E31 E32 E33
retrieval             19/25       6/7     0.0     0.0   fails: E13 E14 E15 E19 E31 E33
llm (stub)            19/25       6/7     0.1     0.3   fails: E13 E14 E15 E19 E31 E33
```

Why a case fails: E31 ("what happens if I pay tuition late") fails because the router matches "tuition" and routes to the deterministic fee calculator ("How many credits?") before retrieval runs, while E33 ("can I renew a borrowed book online") fails because morphological differences ("borrowed"/"book"/"renew" vs. "borrow"/"books"/"renewed") leave BM25 below `min_score=2.0` and trigger abstention.
