# Lab 6 — T7 bonus (han_htg) — optional, pick one

## Option H3
Change `tokenize` in `lab06/starter/src/assistant_core/rag/index.py` to strip a trailing `s` from words longer than
4 letters (on your branch only — the team merges one version).

- Does E14 pass now? No — E14 still fails because stripping the trailing `s` from `"credits"` to `"credit"` matches `"credit"` across multiple chunks without boosting `H26#6.1` ("Credit load") enough to beat the competing chunk.
- What else changed in the table? `retrieval` and `llm (stub)` scores dropped from 16/20 to 15/20 and `abstain ok` dropped from 4/5 to 3/5 because E20 newly failed—stemming a word in E20 caused a spurious BM25 match above `RETRIEVAL_MIN_SCORE=2.0` instead of abstaining.