# Lab 6 — Path comparison (vy_th)

## T4 — base 20 cases

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.3   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.0   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.1     0.4   fails: E13 E14 E15 E19
```

### 3 sentences

(a) For handbook questions, I would use the retrieval path.

(b) I chose retrieval because it achieves the same accuracy as the LLM stub (16/20) while directly quoting official documents without requiring a language model.

(c) I would fix E19 first because the assistant answers a question about open-book exams even though the retrieved documents do not contain the required information.

## T5 — with my 5 H1 cases (E26–E30)

<!-- cd lab06/starter && python eval/compare_paths.py ../../submissions/lab06/vy_th/h1_cases.jsonl -->

```
(paste the output here)
```

Why a case fails: TODO
