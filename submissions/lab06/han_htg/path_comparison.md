# Lab 6 — Path comparison (han_htg)

## T4 — base 20 cases

<!-- cd lab06/starter && python eval/compare_paths.py   — paste everything it prints between the fences. -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     1.8   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.1     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.6     1.2   fails: E13 E14 E15 E19
```

### 3 sentences (exactly one per line, replace TODO)

(a) For handbook questions I would use: the `retrieval` or `llm` path (with A1 abstain and A2 grounding checks enabled), because both score 16/20 whereas the `deterministic` path only scores 7/20 and fails every policy/handbook query.
(b) Because: the `deterministic` path relies solely on rule-based routing and tools without searching the knowledge base, whereas `retrieval` and `llm (stub)` search the KB chunks via BM25 and share the same `RETRIEVAL_MIN_SCORE` gate (A1), producing identical accuracy on the base 20 cases while `llm` adds natural phrasing grounded by A2.
(c) The failure I would fix first (one of E13, E14, E15, E19): E15 ("how long can I keep a library book"), because the keyword router matches "library" and prematurely returns the library's office hours before BM25 retrieval can run and find chunk `S26#1`.

## T5 — with my 5 H1 cases (E46–E50)

<!-- cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/han_htg/h1_cases.jsonl -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.9   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E46 E47 E48      
retrieval             20/25       6/7     0.1     0.1   fails: E13 E14 E15 E19 E46
llm (stub)            20/25       6/7     0.5     2.2   fails: E13 E14 E15 E19 E46
```

Why a case fails: E46 ("What is the replacement fee and processing time for a lost student card?") fails because the keyword router sees the word "fee" and routes the query to the tuition fee calculator tool before BM25 retrieval can run to retrieve chunk `S26#3`.
