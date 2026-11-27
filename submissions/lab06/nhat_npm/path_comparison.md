# Lab 6 — Path comparison (nhat_npm)

## T4 — base 20 cases

<!-- cd lab06/starter && python eval/compare_paths.py   — paste everything it prints between the fences. -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     1.5   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.1     0.2   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.3     1.6   fails: E13 E14 E15 E19
```

### 3 sentences (exactly one per line, replace TODO)

(a) For handbook questions I would use: the llm path because it produces user-friendly, phrased answers while strictly grounding them in retrieved official documents.
(b) Because: it dramatically outperforms the deterministic router (16/20 vs 7/20 correct) while safely falling back to direct retrieval or abstaining when confidence is low.
(c) The failure I would fix first (one of E13, E14, E15, E19): E14, because basic morphological stemming to normalize plural nouns like "credits" to "credit" is straightforward and directly improves retrieval coverage for credit load rules.

## T5 — with my 5 H1 cases (E36–E40)

<!-- cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/nhat_npm/h1_cases.jsonl -->

```
cases: 25 from lab06\starter\eval\cases.jsonl, submissions\lab06\nhat_npm\h1_cases.jsonl
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     3.1   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E36 E37 E38
retrieval             20/25       6/7     0.1     0.9   fails: E13 E14 E15 E19 E36
llm (stub)            20/25       6/7     0.3     3.6   fails: E13 E14 E15 E19 E36
```

Why a case fails: E36 fails on the retrieval and LLM paths because the router's keyword rule matches the word "fee" and routes the query to the tuition calculator rather than delegating to RAG search for campus services.
