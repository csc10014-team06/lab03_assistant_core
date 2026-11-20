# Lab 6 — Path comparison (long_th)

## T4 — base 20 cases

<!-- cd lab06/starter && python eval/compare_paths.py   — paste everything it prints between the fences. -->

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.4   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.0   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.1     0.3   fails: E13 E14 E15 E19
```

### 3 sentences (exactly one per line, replace TODO)

(a) For handbook questions I would use: the retrieval path with the A1 abstain gate, and switch to the llm path only once a real model beats it on this eval (with the stub both score 16/20).
(b) Because: it gets 16/20 against 7/20 for deterministic, every answer quotes a real handbook chunk the student can check, it abstains on 4/5 questions it should not answer, and it runs in under 1 ms with nothing that can invent text.
(c) The failure I would fix first (one of E13, E14, E15, E19): E15, because "how long can I keep a library book" never reaches retrieval: the router sees "library" and returns the office hours, so I would only route to the office lookup for location/opening-hours questions and send the rest to retrieval (the same routing problem breaks E13 and my E23).

## T5 — with my 5 H1 cases (E21–E25)

<!-- cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/long_th/h1_cases.jsonl -->

```
cases: 25 from lab06/starter/eval/cases.jsonl, submissions/lab06/long_th/h1_cases.jsonl
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.4   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             19/25       5/7     0.0     0.1   fails: E13 E14 E15 E19 E23 E25
llm (stub)            19/25       5/7     0.1     0.2   fails: E13 E14 E15 E19 E23 E25
```

Why a case fails: E23 and E25 fail on retrieval and llm: the router sends E23 to the tuition calculator because it contains "fee" (answer: "How many credits?"), and the privacy guard misses E25 because its patterns only match "grades of another student", not "another student's grades", so the assistant answers from S26#3 instead of refusing — a privacy bug the team should fix in `guard.py`.
