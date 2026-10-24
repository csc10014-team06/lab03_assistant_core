"""handbook.py — keyword-scored rule search.

Stub module: implementation owned by truyen_lp.
"""
from __future__ import annotations

from assistant_core.data_loader import Rule


def best_rule(text: str, rules: list[Rule], min_score: int = 1) -> Rule | None:
    """Return the rule with the highest keyword-overlap score for *text*.

    Scores are computed by counting words longer than 3 characters that
    appear in rule["text"] (case-insensitive). Tie-breaking: first entry wins.
    Returns None if no rule scores >= min_score.
    """
    words = [w for w in text.lower().split() if len(w) > 3]
    best: Rule | None = None
    best_score = 0
    for rule in rules:
        score = sum(1 for w in words if w in rule.text.lower())
        if score > best_score:
            best_score = score
            best = rule
    return best if best_score >= min_score else None
