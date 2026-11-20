# Lab 6 — T7 bonus (nhat_npm) — optional, pick one

## Option H3
Change `tokenize` in `lab06/starter/src/assistant_core/rag/index.py` to strip a trailing `s` from words longer than
4 letters (on your branch only — the team merges one version).

- Does E14 pass now? Yes — after stripping the trailing "s", "credits" becomes "credit" which now matches the query "can I take 32 credits" against the document containing "credit load" (H26#6.1). The search correctly retrieves the right chunk.
- What else changed in the table? E13 also improved because "students" in the documents now matches "student" in queries more reliably, but E15 and E19 remain failures since their issues are about routing and ambiguity, not stemming. No existing passing cases broke, so the change is a net improvement.
