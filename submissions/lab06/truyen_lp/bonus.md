# Lab 6 — T7 bonus (truyen_lp) — optional, pick one

## Option H3
Change `tokenize` in `lab06/starter/src/assistant_core/rag/index.py` to strip a trailing `s` from words longer than
4 letters (on your branch only — the team merges one version).

- Does E14 pass now? No, E14 ("can I take 32 credits") still fails on both `retrieval` and `llm (stub)` because `H26#7.2` (2.086, matching "take") still outscores `H26#6.1` (1.425).
- What else changed in the table? On the base 20 cases, `retrieval` and `llm (stub)` dropped from `16/20` (`abstain ok: 4/5`) to `15/20` (`abstain ok: 3/5`) because `E20` ("tell me about exams") began failing: stripping the trailing `s` turned "exams" into "exam", matching `H26#7.2` (score `3.997 >= 2.0`) instead of abstaining. On the 25-case run with `h1_cases.jsonl`, `E33` ("can I renew a borrowed book online") started passing (`19/25` overall with `E20` newly failing). (Note: `index.py` was reverted after this experiment so the individual PR changes only `submissions/lab06/truyen_lp/`.)
