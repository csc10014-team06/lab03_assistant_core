# Lab 6 — T7 bonus (long_th) — optional, pick one

## Option H3

I changed `tokenize` in `lab06/starter/src/assistant_core/rag/index.py` on my machine only (the team merges one H3
version through #61), so the code change is **not** in this PR:

```python
words = [t for t in re.findall(r"\w+", text.lower()) if t not in STOP]
return [w[:-1] if len(w) > 4 and w.endswith("s") else w for w in words]
```

`pytest -q` still gives 42 passed. `python eval/compare_paths.py` before → after:

```
before  retrieval  16/20  4/5  fails: E13 E14 E15 E19
after   retrieval  15/20  3/5  fails: E13 E14 E15 E19 E20      (llm (stub) the same)
with my H1 cases: 19/25 -> 18/25
```

- Does E14 pass now? No. "credits" becomes "credit", but BM25 still ranks `H26#7.2` first (2.086 vs 1.425 for the
  expected `H26#6.1`); E14 is a ranking problem, not a plural problem.
- What else changed in the table? E20 "tell me about exams" broke: "exams" becomes "exam", which now matches the
  exam-absence chunk `H26#7.2` with a score of 3.997 (before: no match at all), so A1 no longer abstains and the
  assistant answers a question that is too vague to answer. H3 makes retrieval *worse* here, so I would not merge it
  as is; if we stem, `RETRIEVAL_MIN_SCORE` has to be re-tuned at the same time.
