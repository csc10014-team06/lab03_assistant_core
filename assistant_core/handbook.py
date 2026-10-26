"""handbook.py — Keyword-scored rule search for student regulations.

Owner: truyen_lp (Lab 3)

Extracted from lines 82–91 of monolith/assistant_monolith.py.
Pure functions with no globals or side-effects, returning an immutable Rule
dataclass rather than a raw dict.
Includes the AI-extension feature for exam absence deadline lookup.
"""
from __future__ import annotations

import re

from assistant_core.data_loader import Rule

# Canonical ID for the exam absence regulation in handbook.json.
_EXAM_ABSENCE_RULE_ID = "H26-7.2"

# Punctuation to strip from word boundaries so queries like "thesis?" still match.
_EDGE_PUNCTUATION = ".,;:!?()[]\"'«»"

# Pattern to dynamically extract destination office and submission deadline from rule text.
_ABSENCE_PATTERN = re.compile(
    r"to the\s+(?P<office>.+?)\s+within\s+(?P<deadline>\d+\s+working\s+days)",
    re.IGNORECASE,
)


def score_rule(text: str, rule: Rule) -> int:
    """Calculate the keyword-overlap score between *text* and *rule*.

    Each word in *text* with more than 3 characters that is contained
    in the rule's text (case-insensitive) contributes 1 to the score.
    Word boundary punctuation is stripped before length evaluation.

    Parameters
    ----------
    text:
        User query or message.
    rule:
        Rule dataclass to score against.

    Returns
    -------
    int:
        Number of matching keywords (>= 0).
    """
    rule_content = rule.text.lower()
    raw_words = text.lower().split()
    score = 0
    for raw_word in raw_words:
        cleaned = raw_word.strip(_EDGE_PUNCTUATION)
        if len(cleaned) > 3 and cleaned in rule_content:
            score += 1
    return score


def best_rule(text: str, rules: list[Rule], min_score: int = 1) -> Rule | None:
    """Find the rule with the highest keyword-overlap score for *text*.

    Tie-breaking: strictly greater score ('>') is used so that when two
    rules achieve the same top score, the first one encountered in *rules*
    wins, preserving monolith behaviour.

    Parameters
    ----------
    text:
        User query or message.
    rules:
        List of Rule dataclasses to search through.
    min_score:
        Minimum score required for a match (default: 1).

    Returns
    -------
    Rule | None:
        The highest-scoring Rule, or None if no rule meets *min_score*.
    """
    best: Rule | None = None
    best_score = 0
    for rule in rules:
        score = score_rule(text, rule)
        if score > best_score:
            best_score = score
            best = rule

    return best if best_score >= min_score else None


# ---------------------------------------------------------------------------
# AI-extension feature: Exam absence answers (reviewed by truyen_lp)
# ---------------------------------------------------------------------------


def find_exam_absence_rule(rules: list[Rule]) -> Rule | None:
    """Find the specific handbook rule covering exam absence.

    Checks the canonical ID (_EXAM_ABSENCE_RULE_ID) first, then falls back
    to keyword retrieval.

    Parameters
    ----------
    rules:
        List of Rule dataclasses loaded from the handbook.

    Returns
    -------
    Rule | None:
        The matching exam absence Rule, or None if not found in *rules*.
    """
    for rule in rules:
        if rule.id == _EXAM_ABSENCE_RULE_ID:
            return rule
    return best_rule("exam absence medical reasons", rules)


def get_exam_absence_deadline(rules: list[Rule]) -> str | None:
    """Extract the evidence submission deadline and office from the exam absence policy.

    The office and deadline are dynamically extracted from rule.text to maintain
    single source of truth.

    Parameters
    ----------
    rules:
        List of Rule dataclasses loaded from the handbook.

    Returns
    -------
    str | None:
        Human-readable summary of the deadline and instructions, or None
        if the absence rule cannot be found.
    """
    rule = find_exam_absence_rule(rules)
    if rule is None:
        return None

    match = _ABSENCE_PATTERN.search(rule.text)
    if match:
        office = match.group("office").strip()
        deadline = match.group("deadline").strip()
        return (
            f"Exam absence deadline: evidence must be submitted within {deadline} "
            f"to the {office} (source: {rule.id})."
        )
    return f"{rule.text} (source: {rule.id})"
