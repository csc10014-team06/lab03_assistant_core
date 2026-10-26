# AI Use Log

Record of AI-assistant usage across the refactoring process (as required by `docs/team-plan.md`).

---

## Member: truyen_lp

### Session 1: Planning and Architecture Review
- **Date**: 2026-10-26
- **Tool**: Antigravity (Gemini 3.8 Flash High)
- **Prompt**: "Bạn hãy đọc qua docs/team-plan.md, mình là truyen_lp. Bạn hãy xem và lập plan thực hiện kế hoạch cho mình."
- **Kept**: Detailed execution plan structuring offices.py lookup, handbook.py scoring, tie-breaking guarantees, dataclass contracts, and test plans.
- **Changed**: Refined tokenization boundary punctuation stripping in `handbook.py` so trailing punctuation (e.g. `thesis?`) does not prevent keyword matching, while strictly preserving monolith tie-breaking logic.

### Session 2: AI-Extension Feature (Exam Absence)
- **Date**: 2026-10-26
- **Tool**: Antigravity (Gemini 3.8 Flash High)
- **Prompt**: "Write a Python function in handbook.py that extracts the exam absence rule and returns a direct answer with the deadline for submitting evidence to the Training Office."
- **Kept**: Core intent of finding rule and providing deadline answer.
- **Changed**:
  1. Replaced hardcoded text with dynamic regex extraction against `Rule.text` from the handbook dataset.
  2. Replaced untyped signature returning string on error with `Rule | None` / `str | None` type hints and proper docstrings.
  3. Replaced fragile `r.title` check with canonical ID `H26-7.2` lookup and pure `best_rule` keyword fallback.
- **Review documented in**: `worksheets/ai_extension_review.md`.
