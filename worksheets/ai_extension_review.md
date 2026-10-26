# Lab 3 — AI extension review

1. Ask an AI coding assistant to extend your service with ONE feature, e.g.
   "Add an 'exam absence' answer that tells students the deadline from the handbook."
2. Paste the prompt you used:
   "Write a Python function in handbook.py that extracts the exam absence rule and returns a direct answer with the deadline for submitting evidence to the Training Office."

3. Review the generated code manually. Document **at least three changes** you made:

| # | What the AI generated | Problem you found | What you changed | Why |
|---|---|---|---|---|
| 1 | Hardcoded return text: `return "Students must submit medical evidence to the Training Office within 3 working days"` | Hardcodes both the submission deadline and the destination office ("to the Training Office"). If university policy or office assignments change in `handbook.json`, hardcoded strings return obsolete data and violate single source of truth. | Extracted both deadline and destination office dynamically from `rule.text` using regex `_ABSENCE_PATTERN = re.compile(r"to the\s+(?P<office>.+?)\s+within\s+(?P<deadline>\d+\s+working\s+days)", re.IGNORECASE)` with fallback to full `rule.text`. | Maintains complete single source of truth from handbook dataset; changes to data files automatically update answers. |
| 2 | Untyped signature returning string on error: `def get_exam_absence(rules): ... return "Rule not found"` | Missing type hints (`Rule`, `list[Rule]`, `str | None`). Returning an error string instead of `None` prevents callers from using idiomatic `if result is not None:` checks. | Added full type annotations `rules: list[Rule] -> str | None` and docstrings; returned `None` when no absence rule exists. | Complies with project-wide strict typing (`ruff`) and allows upstream callers to gracefully fall back without string comparison. |
| 3 | Fragile matching on title: `for r in rules: if "exam absence" in r.title.lower():` | Fails if `title` is modified or missing in handbook data (since schema treats title as optional). | Defined constant `_EXAM_ABSENCE_RULE_ID = "H26-7.2"` to check canonical ID first, with keyword fallback via `best_rule("exam absence medical reasons", rules)`. | Robust against title formatting changes and reuses existing pure keyword scoring without duplicating logic. |

Checklist:
- **Interfaces respected?** Yes. Uses dataclass `Rule` and returns `str | None`.
- **New dependencies?** None. Built exclusively with Python standard library (`re`).
- **Secrets?** None.
- **Logging of user data?** No user data logged or retained.
- **Tests added and meaningful?** Yes, 7 unit tests in `tests/test_handbook.py` under `TestExamAbsenceExtension` testing ID lookup, keyword fallback, dynamic office/deadline regex extraction, missing rule handling, and missing pattern fallback.

Record the use in `docs/ai-use-log.md`.
