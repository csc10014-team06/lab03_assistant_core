# Lab 6 — T7 bonus (vy_th)

## Option Ollama

### Environment

- Model: Llama 3.2
- Ollama version: 0.40.16
- Platform: macOS, Apple Silicon, 18 GB RAM
- Model size: 2.0 GB

### Sample question

Question: Can I register my thesis with 118 credits?

```text
No
  source: H26#5.3 — 5.3 Thesis registration
```

The answer is correct and cites the expected source, although it does not explain the minimum requirement of 120 credits.

### Evaluation results

Command:

```bash
LLM_PROVIDER=ollama LLM_MODEL=llama3.2 python eval/compare_paths.py
```

Output:

```text
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.5   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.0   fails: E13 E14 E15 E19
llm (ollama)          17/20       4/5   828.2  1307.9   fails: E13 E15 E19
```

### Comparison with StubLLM

| Metric | StubLLM | Ollama |
|---|---:|---:|
| Correct | 16/20 | 17/20 |
| Abstain ok | 4/5 | 4/5 |
| p50 latency (ms) | 0.1 | 828.2 |
| Maximum latency (ms) | 0.4 | 1307.9 |

### Observations

- **Slower than the stub?** Yes, Ollama takes considerably longer because it generates answers using a real language model.
- **Did E19 become "I don't know"?** No, E19 still fails, showing that a real language model does not automatically solve the problem of answering unsupported questions.
- **Did any case get worse?** No previously correct case failed in this run, and E14 improved from fail to pass.

### Personal reflection

When I first asked Ollama "What is RAG?", it produced several unrelated definitions. After I specified Retrieval-Augmented Generation in artificial intelligence, its answer became more relevant. This experiment helped me understand the importance of providing appropriate context to a language model.

Although Ollama achieved higher accuracy than the stub in this experiment, it was slower and still failed E19. Therefore, using a real model does not eliminate the need for retrieval, grounding checks, and safe abstention.
