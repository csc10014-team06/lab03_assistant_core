# Lab 6 — Path comparison (nhat_dm)

## T4 — base 20 cases

<!-- cd lab06/starter && python eval/compare_paths.py   — paste everything it prints between the fences. -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.8   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.2     0.7   fails: E13 E14 E15 E19
```

### 3 sentences (exactly one per line, replace TODO)

(a) For handbook questions I would use: the retrieval path with grounding verification.
(b) Because: it directly returns verified citations from the knowledge base with high accuracy (16/20) and negligible latency (0.0 ms p50) without relying on generative stubs.
(c) The failure I would fix first (one of E13, E14, E15, E19): E14, by adding basic stemming to the tokenizer so that plural words like 'credits' match singular heading terms like 'credit load' in chunk H26#6.1.

## T5 — with my 5 H1 cases (E41–E45)

<!-- cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/nhat_dm/h1_cases.jsonl -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E41 E42 E43
retrieval             21/25       6/7     0.1     0.1   fails: E13 E14 E15 E19
llm (stub)            21/25       6/7     0.3     0.9   fails: E13 E14 E15 E19
```

Why a case fails: Cases E41, E42, and E43 fail under the deterministic path because it lacks knowledge base search and never answers handbook questions from documents, while E19 fails on retrieval because an ambiguous query matches general exam chunks above min_score rather than abstaining.
