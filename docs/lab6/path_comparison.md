# Lab 6 — Team baseline: deterministic vs retrieval vs llm

Generated with `cd lab06/starter && python eval/compare_paths.py` (offline, stub provider, BM25,
`RETRIEVAL_MIN_SCORE=2.0`, A1/A2 filled in). Re-generate after every change to `lab06/starter` and before tagging
`v0.6-ai`. To include every member's H1 cases, add `--include-submissions`.

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.5   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.1     0.3   fails: E13 E14 E15 E19
```

| path | what it does |
|---|---|
| deterministic | router + tools only; handbook questions are never answered from documents |
| retrieval | router + tools + BM25, quotes the best chunk; abstains below `RETRIEVAL_MIN_SCORE` (A1) |
| llm (stub) | retrieval + model drafting structured JSON; the draft is only shown if it cites retrieved chunks (A2) |

## The four expected failures (retrieval and llm)

| case | question | expected | what actually happens (checked with BM25 + the service) |
|---|---|---|---|
| E13 | when is tuition due | `F26#3` | the **router** sees "tuition" and sends it to the fee tool → "How many credits?"; retrieval never runs (BM25 would also rank `F26#1` above `F26#3`) |
| E14 | can I take 32 credits | `H26#6.1` | retrieval runs but the **wrong chunk wins**: `H26#7.2` (2.09) beats `H26#6.1` (1.48); nothing in the KB says "32" |
| E15 | how long can I keep a library book | `S26#1` | the **router** sees "library" and answers with the office hours; retrieval alone would have found `S26#1` |
| E19 | is the final exam open-book | abstain | "final exam" matches `H26#7.2` strongly (5.62 ≥ 2.0), so A1 lets it through and the stub answers. The KB never says whether exams are open-book; a real model following the prompt might abstain (Ollama bonus) |

Each member explains one of these in T4 (c). Two are routing problems (E13, E15), one is a ranking problem (E14) and
one is a missing "this is not in the documents" check (E19). These need different fixes: a router that lets
handbook-style questions reach retrieval, better ranking (synonyms, hybrid retrieval, H3-style normalisation), and an
abstain rule that looks at more than the top score.
